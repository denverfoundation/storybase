"""REST API for Stories"""

from django.conf import settings
from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import NoReverseMatch
from django.dispatch import receiver, Signal
from django.http import HttpResponse

from haystack.query import SearchQuerySet
from haystack.utils.geo import D, Point

from tastypie import fields, http
from tastypie.bundle import Bundle
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.resources import ModelResource, convert_post_to_put, convert_post_to_patch, NOT_AVAILABLE
from tastypie.utils import trailing_slash
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization

from storybase.utils import get_language_name
from storybase_geo.models import Place
from storybase_story.models import Story, Section
from storybase_taxonomy.models import Category
from storybase_user.models import Organization, Project


class LoggedInAuthorization(Authorization):
    """Custom authorization that checks Django authentication"""
    def is_authorized(self, request, object=None):
        # GET-style methods are always allowed.
        if request.method in ('GET', 'OPTIONS', 'HEAD'):
            return True

        # Users must be logged-in and active in order to use
        # non-GET-style methods
        if (not hasattr(request, 'user') or
            not request.user.is_authenticated or 
            not request.user.is_active):
            return False

        # Logged in users can create new objects
        if request.method in ('POST') and object is None:
            return True

        permission_map = {
            'POST': ['add'],
            'PUT': ['change'],
            'DELETE': ['delete'],
            'PATCH': ['add', 'change', 'delete'],
        }
        permission_codes = permission_map[request.method]

        if hasattr(object, 'has_perms'):
            # If the object supports row-level permissions,
            return object.has_perms(request.user, permission_codes)

        # Fall-back to failure
        return False 

# Signals sent by HookedModelResource
post_bundle_obj_construct = Signal(providing_args=["bundle", "request"])
"""Signal sent after the object is constructed, but not saved"""
pre_bundle_obj_hydrate = Signal(providing_args=["bundle", "request"])
"""Signal sent before the bundle is hydrated"""
post_bundle_obj_hydrate = Signal(providing_args=["bundle", "request"])
"""Signal sent after the bundle is hydrated"""
post_bundle_obj_save = Signal(providing_args=["bundle", "request"])
"""Signal sent after the bundle is saved"""
post_obj_get = Signal(providing_args=["request", "object"])

class HookedModelResource(ModelResource):
    """
    A version of ModelResource with extra actions at various points in the pipeline
    
    This allows for doing things like creating related translation model
    instances or doing row-level authorization checks in a DRY way since
    most of the logic for the core logic of the request/response cycle
    remains the same as ModelResource.

    The hooks are implemented using Django's signal framework.  In this case
    the resource is sending a signal to itself and the signal handlers
    are defined as methods of the HookedModelResource subclass.  Because
    of this, the signature for these methods has an initial argument of
    sender instead of the conventional self, even though its referring
    to the resource object.

    """
    def _bundle_setattr(self, bundle, key, value):
        setattr(bundle.obj, key, value)

    def full_hydrate(self, bundle):
        """
        Given a populated bundle, distill it and turn it back into
        a full-fledged object instance.
        """
        if bundle.obj is None:
            bundle.obj = self._meta.object_class()
            post_bundle_obj_construct.send(sender=self, bundle=bundle, request=None) 
        bundle = self.hydrate(bundle)
        post_bundle_obj_hydrate.send(sender=self, bundle=bundle, request=None)
        for field_name, field_object in self.fields.items():
            if field_object.readonly is True:
                continue

            # Check for an optional method to do further hydration.
            method = getattr(self, "hydrate_%s" % field_name, None)

            if method:
                bundle = method(bundle)
            if field_object.attribute:
                value = field_object.hydrate(bundle)

                # NOTE: We only get back a bundle when it is related field.
                if isinstance(value, Bundle) and value.errors.get(field_name):
                    bundle.errors[field_name] = value.errors[field_name]

                if value is not None or field_object.null:
                    # We need to avoid populating M2M data here as that will
                    # cause things to blow up.
                    if not getattr(field_object, 'is_related', False):
                        self._bundle_setattr(bundle, field_object.attribute, value)
                    elif not getattr(field_object, 'is_m2m', False):
                        if value is not None:
                            setattr(bundle.obj, field_object.attribute, value.obj)
                        elif field_object.blank:
                            continue
                        elif field_object.null:
                            setattr(bundle.obj, field_object.attribute, value)

        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """

        bundle.obj = self._meta.object_class()
        post_bundle_obj_construct.send(sender=self, bundle=bundle, request=request, **kwargs)

        for key, value in kwargs.items():
            self._bundle_setattr(bundle, key, value)
        pre_bundle_obj_hydrate.send(sender=self, bundle=bundle, request=request, **kwargs)
        bundle = self.full_hydrate(bundle)
        self.is_valid(bundle,request)

        if bundle.errors:
            self.error_response(bundle.errors, request)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save parent
        bundle.obj.save()
        post_bundle_obj_save.send(sender=self, bundle=bundle, request=request, **kwargs)

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        if not bundle.obj or not bundle.obj.pk:
            # Attempt to hydrate data from kwargs before doing a lookup for the object.
            # This step is needed so certain values (like datetime) will pass model validation.
            try:
                bundle.obj = self.get_object_list(bundle.request).model()
                post_bundle_obj_construct.send(sender=self, bundle=bundle, request=request, **kwargs)
                bundle.data.update(kwargs)
                bundle = self.full_hydrate(bundle)
                lookup_kwargs = kwargs.copy()

                for key in kwargs.keys():
                    if key == 'pk':
                        continue
                    elif getattr(bundle.obj, key, NOT_AVAILABLE) is not NOT_AVAILABLE:
                        lookup_kwargs[key] = getattr(bundle.obj, key)
                    else:
                        del lookup_kwargs[key]
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs

            try:
                bundle.obj = self.obj_get(bundle.request, **lookup_kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        bundle = self.full_hydrate(bundle)
        self.is_valid(bundle,request)

        if bundle.errors and not skip_errors:
            self.error_response(bundle.errors, request)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()
        post_bundle_obj_save.send(sender=self, bundle=bundle, request=request, **kwargs)

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

    def patch_detail(self, request, **kwargs):
        """
        Updates a resource in-place.

        Calls ``obj_update``.

        If the resource is updated, return ``HttpAccepted`` (202 Accepted).
        If the resource did not exist, return ``HttpNotFound`` (404 Not Found).
        """
        request = convert_post_to_patch(request)

        # We want to be able to validate the update, but we can't just pass
        # the partial data into the validator since all data needs to be
        # present. Instead, we basically simulate a PUT by pulling out the
        # original data and updating it in-place.
        # So first pull out the original object. This is essentially
        # ``get_detail``.
        try:
            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        # Send a signal
        post_obj_get.send(sender=self, request=request, obj=obj)

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)

        # Now update the bundle in-place.
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        try:
            self.update_in_place(request, bundle, deserialized)
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        if not self._meta.always_return_data:
            return http.HttpAccepted()
        else:
            bundle = self.full_dehydrate(bundle)
            bundle = self.alter_detail_data_to_serialize(request, bundle)
            return self.create_response(request, bundle, response_class=http.HttpAccepted)


class TranslatedModelResource(HookedModelResource):
    """A version of ModelResource that handles our translation implementation"""
    # This is a write-only field that we include to allow specifying the
    # language when creating an object.  We remove it from the response in
    # dehydrate()
    language = fields.CharField(attribute='language', default=settings.LANGUAGE_CODE)
    languages = fields.ListField(readonly=True)

    def dehydrate(self, bundle):
        # Remove the language field since it doesn't make sense in the response
        del bundle.data['language']
        return bundle

    def dehydrate_languages(self, bundle):
        return bundle.obj.get_language_info()

    @receiver(post_bundle_obj_construct)
    def translation_obj_construct(sender, bundle, request, **kwargs):
        """
        Create a translation object and add it to the bundle
        
        This should be connected to the ``post_bundle_obj_construct`` signal

        """
        translation_class = sender._meta.object_class.translation_class
        bundle.translation_obj = translation_class()

    @receiver(post_bundle_obj_save)
    def translation_obj_save(sender, bundle, request, **kwargs):
        """
        Associate the translation object with its parent and save

        This should be connected to the ``post_bundle_obj_save`` signal

        """
        object_class = sender._meta.object_class
        # Associate and save the translation
        fk_field_name = object_class.get_translation_fk_field_name()
        setattr(bundle.translation_obj, fk_field_name, bundle.obj)
        bundle.translation_obj.save()

    @receiver(post_bundle_obj_hydrate)
    def translation_obj_get(sender, bundle, request, **kwargs):
        """
        Get the associated translation model instance

        This should be connected to the ``post_bundle_obj_hydrate``
        signal.

        """
        if bundle.obj.pk and not hasattr(bundle, 'translation_obj'):
            language = bundle.data.get('language', sender.fields['language'].default)
            translation_set = getattr(bundle.obj, bundle.obj.translation_set)
            bundle.translation_obj = translation_set.get(language=language)

    def _get_translation_fields(self):
        return self._meta.object_class.translated_fields + ['language']

    def _bundle_setattr(self, bundle, key, value):
        if not hasattr(bundle, 'translation_fields'):
            bundle.translation_fields = self._get_translation_fields() 

        if key in bundle.translation_fields: 
            setattr(bundle.translation_obj, key, value)
        else:
            setattr(bundle.obj, key, value)


class DelayedAuthorizationResource(TranslatedModelResource):
    def dispatch(self, request_type, request, **kwargs):
        """
        Handles the common operations (allowed HTTP method, authentication,
        throttling, method lookup) surrounding most CRUD interactions.

        This version moves the authorization check to later in the pipeline
        """
        allowed_methods = getattr(self._meta, "%s_allowed_methods" % request_type, None)
        request_method = self.method_check(request, allowed=allowed_methods)
        method_name = "%s_%s" % (request_method, request_type)
        method = getattr(self, method_name, None)

        if method is None:
            raise ImmediateHttpResponse(response=http.HttpNotImplemented())

        self.is_authenticated(request)
        if method_name not in self._meta.delayed_authorization_methods:
            self.is_authorized(request)
        self.throttle_check(request)

        # All clear. Process the request.
        request = convert_post_to_put(request)
        response = method(request, **kwargs)

        # Add the throttled request.
        self.log_throttled_access(request)

        # If what comes back isn't a ``HttpResponse``, assume that the
        # request was accepted and that some action occurred. This also
        # prevents Django from freaking out.
        if not isinstance(response, HttpResponse):
            return http.HttpNoContent()

        return response

    @receiver(pre_bundle_obj_hydrate)
    def check_bundle_obj_authorization(sender, bundle, request, **kwargs):
        """
        Check authorization of the bundle's object
        
        Simply calls through to is_authorized.

        This should be connected to the ``pre_bundle_obj_hydrate`` signal.

        """
        sender.is_authorized(request, bundle.obj)

    @receiver(post_obj_get)
    def check_obj_authorization(sender, request, obj, **kwargs):
        """
        Check authorization of an object based on the request

        Simply calls through to the is_authorized method of the resource

        This should be connected to the ``post_obj_get`` signal.

        """
        sender.is_authorized(request, obj)


class StoryResource(DelayedAuthorizationResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title')
    summary = fields.CharField(attribute='summary')
    url = fields.CharField(attribute='get_absolute_url')
    sections = fields.ToManyField('storybase_story.api.SectionResource', 'sections', readonly=True)
    topics = fields.ListField(readonly=True)
    organizations = fields.ListField(readonly=True)
    projects = fields.ListField(readonly=True)
    # A list of lat/lon values for related Location objects as well as
    # centroids of Place tags
    points = fields.ListField(readonly=True)

    class Meta:
        queryset = Story.objects.all()
        resource_name = 'stories'
        allowed_methods = ['get', 'post', 'patch']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        # Hide the underlying id
        excludes = ['id']
        filtering = {
            'story_id': ALL, 
        }

        # Custom meta attributes
        # Methods that handle authorization later than normain in the flow
        delayed_authorization_methods = ('patch_detail',)
        # Filter arguments for custom explore endpoint
        explore_filter_fields = ['topics', 'projects', 'organizations', 'languages', 'places']
        explore_point_field = 'points'

   
    # TODO: If not using the development branch of tastypie, uncomment this
    # as the prepend_urls was called override_urls in previous versions. This
    # code can be removed altogether when Tastypie reaches 1.0
    #def override_urls(self):
    #    return self.prepend_urls()

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/explore%s$'  % (self._meta.resource_name, trailing_slash()), self.wrap_view('explore_get_list'), name="api_explore_get_list"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/sections/$" % self._meta.resource_name, self.wrap_view('dispatch_section_list'), name="api_dispatch_list_sections"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/sections/(?P<section_id>[0-9a-f]{32,32})/$" % self._meta.resource_name, self.wrap_view('dispatch_section_detail'), name="api_dispatch_detail_sections"),
        ]

    def detail_uri_kwargs(self, bundle_or_obj):
        """
        Given a ``Bundle`` or an object (typically a ``Model`` instance),
        it returns the extra kwargs needed to generate a detail URI.

        This version returns the story_id field instead of the pk
        """
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.obj.story_id
        else:
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.story_id

        return kwargs


    def get_object_list(self, request):
        """Get a list of stories, filtering based on the request's user"""
        from django.db.models import Q
        # Only show published stories  
        q = Q(status='published')
        if hasattr(request, 'user') and request.user.is_authenticated():
            # If the user is logged in, show their unpublished stories as
            # well
            q = q | Q(author=request.user)

        return super(StoryResource, self).get_object_list(request).filter(q)


    def obj_create(self, bundle, request=None, **kwargs):
        # Set the story's author to the request's user
        if request.user:
            kwargs['author'] = request.user
        return super(StoryResource, self).obj_create(bundle, request, **kwargs)

    def dehydrate_topics(self, bundle):
        """Populate a list of topic ids and names in the response objects"""
        return [{ 'id': topic.pk, 'name': topic.name }
                for topic in bundle.obj.topics.all()]

    def dehydrate_organizations(self, bundle):
        """
        Populate a list of organization ids and names in the response objects
        """
        return [{ 'id': organization.organization_id, 'name': organization.name }
                for organization in bundle.obj.organizations.all()]

    def dehydrate_projects(self, bundle):
        """
        Populate a list of project ids and names in the response objects
        """
        return [{ 'id': project.project_id, 'name': project.name }
                for project in bundle.obj.projects.all()]

    def dehydrate_places(self, bundle):
        """
        Populate a list of place ids and names in the response objects
        """
        return [{ 'id': place.place_id, 'name': place.name }
                for place in bundle.obj.inherited_places]

    def dehydrate_points(self, bundle):
        """
        Populate a list of geographic points in the response object
        """
        return [point for point in bundle.obj.points]

    def _get_facet_field_name(self, field_name):
        """Convert public filter name to underlying Haystack index field"""
        return field_name.rstrip('s') + '_ids'

    def _get_filter_field_name(self, field_name):
        """Convert underlying Haystack index field to public filter name"""
        return field_name.rstrip('_ids') + 's'

    def _get_facet_choices(self, field_name, items):
        """Build tuples of ids and human readable strings for a given facet"""
        getter_fn = getattr(self, '_get_facet_choices_%s' % field_name)
        return getter_fn(items)

    def _get_facet_choices_topic_ids(self, items):
        return [{ 'id': obj.pk, 'name': obj.name } 
                for obj in Category.objects.filter(pk__in=items)\
                                           .order_by('categorytranslation__name')]

    def _get_facet_choices_project_ids(self, items):
        return [{ 'id': obj.project_id, 'name': obj.name }
                for obj in Project.objects.filter(project_id__in=items)\
                                          .order_by('projecttranslation__name')]

    def _get_facet_choices_organization_ids(self, items):
        return [{ 'id': obj.organization_id, 'name': obj.name}
                for obj in Organization.objects.filter(organization_id__in=items)\
                                               .order_by('organizationtranslation__name')]

    def _get_facet_choices_language_ids(self, items):
        return sorted([{ 'id': item, 'name': get_language_name(item)} 
                       for item in items],
                       key=lambda language: language['name'])

    def _get_facet_choices_place_ids(self, items):
        return [{ 'id': obj.place_id, 'name': obj.name }
                for obj in Place.objects.filter(place_id__in=items)\
                                        .order_by('name')]

    def explore_get_result_list(self, request):
        sqs = SearchQuerySet().models(Story)
        filter_fields = self._meta.explore_filter_fields
        for filter_field in filter_fields:
            facet_field = self._get_facet_field_name(filter_field)
            sqs = sqs.facet(facet_field)

        return sqs

    def explore_build_filters(self, filters=None):
        def _get_num_points_filter(filters):
            for suffix in ('__gt', '__gte', '__lt', '__lte'):
                filter_name = "%s%s" % ("num_points", suffix)
                filter_value = filters.get(filter_name, None)
                if filter_value is not None:
                    return (filter_name, filter_value)
            else:
                return (None, None)
                
        applicable_filters = {}
        filter_fields = self._meta.explore_filter_fields
        for filter_field in filter_fields:
            facet_field = self._get_facet_field_name(filter_field)
            filter_values = filters.get(filter_field, None)
            if filter_values:
                applicable_filters['%s__in' % facet_field] = filter_values.split(',')

        (num_points_filter_name, num_points_filter_value) =  _get_num_points_filter(filters)
        if num_points_filter_name:
            applicable_filters[num_points_filter_name] = int(num_points_filter_value)

            
        return applicable_filters

    def _explore_spatial_filter_object_list(self, request, object_list):
        """Apply spatial filters to object list"""
        def _parse_near_param(s):
            """
            Parse the ``near`` query string parameter

            The parameter should be of the form lat@lng,miles 

            Returns a tuple of a Point and D object suitable for passing
            to ``SearchQuerySet.dwithin()``

            """
            (latlng, dist) = s.split(',')
            (lat, lng) = latlng.split('@')
            return (Point(float(lng), float(lat)),  D(mi=dist))

        near_param = request.GET.get('near', None)
        if near_param:
            (point, dist) = _parse_near_param(near_param)
            proximity_filtered_object_list = object_list.dwithin(self._meta.explore_point_field, point, dist).distance(self._meta.explore_point_field, point)
            return proximity_filtered_object_list 

        else:
            return object_list

    def explore_apply_filters(self, request, applicable_filters):
        object_list = self.explore_get_result_list(request)
        object_list = self._explore_spatial_filter_object_list(request, object_list)
        if applicable_filters:
            object_list = object_list.filter(**applicable_filters)

        return object_list.order_by('-published').load_all()
        
    def explore_result_get_list(self, request=None, **kwargs):
        filters = {}

        if hasattr(request, 'GET'):
            # Grab a mutable copy.
            filters = request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)
        applicable_filters = self.explore_build_filters(filters=filters)
        results = self.explore_apply_filters(request, applicable_filters)
        return results

    def explore_get_resource_list_uri(self):
        """
        Returns a URL specific to this resource's list endpoint.
        """
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        try:
            return self._build_reverse_url("api_explore_get_list", kwargs=kwargs)
        except NoReverseMatch:
            return None

    def _add_boundaries(self, request, to_be_serialized):
        """
        Add boundaries field to data to be seriazlized
        """
        boundaries = []
        specified_places = request.GET.get('places', None)
        if specified_places and to_be_serialized['places']:
            specified_place_ids = specified_places.split(",")
            for place in to_be_serialized['places']:
                if place['id'] in specified_place_ids:
                    place = Place.objects.get(place_id=place['id'])
                    boundary = place.boundary
                    if boundary:
                        coords = boundary.coords
                        boundary = [coords[0][i]
                                    for i in range(boundary.num_geom)]
                        boundaries.append(boundary)
        to_be_serialized['boundaries'] = boundaries

    def explore_get_data_to_be_serialized(self, request=None, **kwargs):
        """
        Helper to build a filtered and paginated list of stories and
        facet and paging metadta

        This is broken out of ``explore_get_list`` so it can be called
        from other views, often to bootstrap JavaScript objects.

        """
        resource_uri = self.explore_get_resource_list_uri()
        objects = []
        results = self.explore_result_get_list(request, **kwargs)
        request_data = {}
        if hasattr(request, 'GET'):
            request_data = request.GET

        for result in results:
            bundle = self.build_bundle(obj=result.object, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        paginator = self._meta.paginator_class(request_data, objects,
                                               resource_uri=resource_uri,
                                               limit=self._meta.limit)
        to_be_serialized = paginator.page()

        # Add the resource URI to the response metadata so the client-side
        # code can be naive
        to_be_serialized['meta']['resource_uri'] = resource_uri 

        for facet_field, items in results.facet_counts()['fields'].iteritems():
            filter_field = self._get_filter_field_name(facet_field)
            to_be_serialized[filter_field] = self._get_facet_choices(
                facet_field, [item[0] for item in items if item[1] > 0])

        self._add_boundaries(request, to_be_serialized)

        return to_be_serialized
            
    def explore_get_list(self, request, **kwargs):
        """Custom endpoint to drive the drill-down in the "Explore" view"""
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        to_be_serialized = self.explore_get_data_to_be_serialized(
            request, **kwargs)

        return self.create_response(request, to_be_serialized)

    def dispatch_section_detail(self, request, **kwargs):
        try:
            # Remove the section id from the keyword arguments to lookup the
            # the story, saving it to pass to SectionResource.dispatch_detail
            # later
            section_id = kwargs.pop('section_id')
            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        section_resource = SectionResource()
        return section_resource.dispatch_detail(request, story_id=obj.story_id,
                                                section_id=section_id)

    def dispatch_section_list(self, request, **kwargs):
        try:
            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        section_resource = SectionResource()
        return section_resource.dispatch_list(request, story_id=obj.story_id)


class SectionResource(DelayedAuthorizationResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title')
    story = fields.ToOneField(StoryResource, 'story')

    class Meta:
        queryset = Section.objects.all()
        resource_name = 'sections'
        allowed_methods = ['get', 'post', 'patch']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        # Hide the underlying id
        excludes = ['id']
        filtering = {
            'story': ALL_WITH_RELATIONS,
        }

        # Custom meta attributes
        # Class of the resource under which this is nested
        parent_resource = StoryResource
        # Methods that handle authorization later than normain in the flow
        delayed_authorization_methods = ('patch_detail',)

    def detail_uri_kwargs(self, bundle_or_obj):
        """
        Given a ``Bundle`` or an object (typically a ``Model`` instance),
        it returns the extra kwargs needed to generate a detail URI.

        This version returns the section_id field instead of the pk
        as well as the related story's story_id

        """
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            obj = bundle_or_obj.obj 
        else:
            obj = bundle_or_obj

        kwargs['section_id'] = obj.section_id
        kwargs['story_id'] = obj.story.story_id

        return kwargs

    def resource_uri_kwargs(self, bundle_or_obj=None):
        """
        Builds a dictionary of kwargs to help generate URIs.

        This retrieves the resource_name and api_name from the parent resource
        as this resource is designed to be nested under ``StoryResource``

        """
        kwargs = super(SectionResource, self).resource_uri_kwargs(bundle_or_obj)
        kwargs['resource_name'] = self._meta.parent_resource._meta.resource_name 
        if self._meta.parent_resource._meta.api_name is not None:
            kwargs['api_name'] = self._meta.parent_resource._meta.api_name
        return kwargs

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):
        """
        Handles generating a resource URI.

        This version appends the resource name to the URL name so it can
        be looked up in the URIs defined in ``StoryResource.prepend_urls``

        """
        if bundle_or_obj is not None:
            url_name = 'api_dispatch_detail'

        nested_url_name = url_name + "_%s" % (self._meta.resource_name)

        try:
            kwargs = self.resource_uri_kwargs(bundle_or_obj)
            return self._build_reverse_url(nested_url_name, kwargs=kwargs)
        except NoReverseMatch:
            return ''

    def obj_create(self, bundle, request=None, **kwargs):
        story_id = kwargs.pop('story_id')
        kwargs['story'] = Story.objects.get(story_id=story_id)
        return super(SectionResource, self).obj_create(bundle, request, **kwargs)

    def obj_get(self, request=None, **kwargs):
        story_id = kwargs.pop('story_id')
        kwargs['story'] = Story.objects.get(story_id=story_id)
        return super(SectionResource, self).obj_get(request, **kwargs)
