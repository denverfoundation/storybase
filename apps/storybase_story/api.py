"""REST API for Stories"""
import logging

from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import NoReverseMatch
from django.db import transaction, IntegrityError
from django.db.models import Q
try:
    from django.utils import timezone
except ImportError:
    from storybase.utils import timezone

from haystack.query import SearchQuerySet
from haystack.utils.geo import D, Point

from tastypie import fields, http
from tastypie.authentication import Authentication
from tastypie.bundle import Bundle
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, ImmediateHttpResponse, Unauthorized
from tastypie.utils import dict_strip_unicode_keys, trailing_slash

from storybase.api import (HookedModelResource, TranslatedModelResource,
                           LoggedInAuthorization, PublishedOwnerAuthorization)
from storybase.utils import get_language_name
from storybase_asset.api import AssetResource
from storybase_geo.models import Place
from storybase_help.models import Help
from storybase_story.models import (Container, ContainerTemplate,
                                    Section, SectionAsset, SectionLayout, 
                                    Story, StoryRelation, StoryTemplate)
from storybase_taxonomy.models import Category
from storybase_user.models import Organization, Project

logger = logging.getLogger("storybase")

class StoryAuthorization(PublishedOwnerAuthorization):
    owner_field = 'author'

class StoryResource(TranslatedModelResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title', blank=True)
    summary = fields.CharField(attribute='summary', blank=True)
    call_to_action = fields.CharField(attribute='call_to_action', blank=True)
    connected_prompt = fields.CharField(attribute='connected_prompt',
                                        blank=True)
    url = fields.CharField(attribute='get_absolute_url', readonly=True)
    topics = fields.ListField(readonly=True)
    organizations = fields.ListField(readonly=True)
    projects = fields.ListField(readonly=True)
    places = fields.ListField(readonly=True)
    featured_asset_url = fields.CharField(readonly=True)
    connected_count = fields.IntegerField(attribute='connected_count',
            readonly=True)
    # A list of lat/lon values for related Location objects as well as
    # centroids of Place tags
    points = fields.ListField(readonly=True)
    template_story = fields.CharField(attribute='template_story',
        null=True)

    class Meta:
        always_return_data = True
        queryset = Story.objects.all()
        resource_name = 'stories'
        allowed_methods = ['get', 'post', 'patch', 'put']
        authentication = Authentication()
        authorization = StoryAuthorization()
        # Hide the underlying id
        excludes = ['id']
        filtering = {
            'story_id': ALL, 
        }

        # Custom meta attributes
        # Filter arguments for custom explore endpoint
        explore_filter_fields = ['topics', 'projects', 'organizations', 'languages', 'places']
        explore_point_field = 'points'

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/explore%s$'  % (self._meta.resource_name, trailing_slash()), self.wrap_view('explore_get_list'), name="api_explore_get_list"),
            url(r'^(?P<resource_name>%s)/templates%s$'  % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_template_list'), name="api_dispatch_list_templates"),
            url(r'^(?P<resource_name>%s)/templates/(?P<template_id>[0-9a-f]{32,32})%s$'  % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_template_detail'), name="api_dispatch_detail_templates"),
            url(r'^(?P<resource_name>%s)/containertemplates/templates/(?P<template_id>[0-9a-f]{32,32})%s$'  % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_container_template_list'), name="api_dispatch_list_containertemplates"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/sections%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_section_list'), name="api_dispatch_list_sections"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/sections/(?P<section_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_section_detail'), name="api_dispatch_detail_sections"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/sections/(?P<section_id>[0-9a-f]{32,32})/assets%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_sectionasset_list'), name="api_dispatch_list_sectionassets"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/sections/(?P<section_id>[0-9a-f]{32,32})/assets/(?P<asset_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_sectionasset_detail'), name="api_dispatch_detail_sectionassets"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/topics%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_storycategory_list'), name="api_dispatch_list_storycategories"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/places%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_storyplace_list'), name="api_dispatch_list_storyplaces"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/organizations%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_storyorganization_list'), name="api_dispatch_list_storyorganizations"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/organizations%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_storyorganization_list'), name="api_dispatch_list_storyorganizations"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/projects%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_storyproject_list'), name="api_dispatch_list_storyprojects"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/related%s" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_storyrelation_list'), name="api_dispatch_list_storyrelations"),
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

    def obj_create(self, bundle, **kwargs):
        # Set the story's author to the request's user
        if bundle.request.user.is_authenticated():
            kwargs['author'] = bundle.request.user
        return super(StoryResource, self).obj_create(bundle, **kwargs)

    def dehydrate_template_story(self, bundle):
        if bundle.obj.template_story:
            return bundle.obj.template_story.story_id
        else:
            return None

    def hydrate_template_story(self, bundle):
        template_story = bundle.data.get('template_story', None)
        if template_story and not isinstance(template_story, Story):
            bundle.data['template_story'] = Story.objects.get(story_id=template_story)
        return bundle

    def dehydrate_topics(self, bundle):
        """Populate a list of topic ids and names in the response objects"""
        return bundle.obj.topics_list()

    def dehydrate_organizations(self, bundle):
        """
        Populate a list of organization ids and names in the response objects
        """
        return bundle.obj.organizations_list()

    def dehydrate_projects(self, bundle):
        """
        Populate a list of project ids and names in the response objects
        """
        return bundle.obj.projects_list()

    def dehydrate_places(self, bundle):
        """
        Populate a list of place ids and names in the response objects
        """
        return bundle.obj.places_list()

    def dehydrate_points(self, bundle):
        """
        Populate a list of geographic points in the response object
        """
        return bundle.obj.points

    def dehydrate_last_edited(self, bundle):
        """
        Add time zone to last_edited date
        """
        tz = timezone.get_default_timezone()
        return timezone.make_aware(bundle.data['last_edited'], tz)

    def dehydrate_featured_asset_url(self, bundle):
        return bundle.obj.featured_asset_thumbnail_url(include_host=False)

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
        return [{ 'id': obj['place_id'], 'name': obj['name'] }
                for obj in Place.objects.filter(place_id__in=items)\
                                        .order_by('name')\
                                        .values('place_id', 'name')]

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
            base_bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        section_resource = SectionResource()
        return section_resource.dispatch_detail(request, 
                                                story__story_id=obj.story_id,
                                                section_id=section_id)

    def dispatch_section_list(self, request, **kwargs):
        try:
            base_bundle = self.build_bundle(request=request)
            obj = self.cached_obj_get(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        section_resource = SectionResource()
        return section_resource.dispatch_list(request, story__story_id=obj.story_id)

    def dispatch_sectionasset_list(self, request, **kwargs):
        try:
            section_id = kwargs.pop('section_id')
            # We fetch the story just to check that the
            # story_id to which the sub-resource is related
            # exists
            base_bundle = self.build_bundle(request=request)
            story = self.cached_obj_get(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        resource = SectionAssetResource()
        return resource.dispatch_list(request, 
            section__section_id=section_id)

    def dispatch_sectionasset_detail(self, request, **kwargs):
        try:
            section_id = kwargs.pop('section_id')
            asset_id = kwargs.pop('asset_id')
            # We fetch the story just to check that the
            # story_id to which the sub-resource is related
            # exists
            base_bundle = self.build_bundle(request=request)
            story = self.cached_obj_get(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        resource = SectionAssetResource()
        return resource.dispatch_detail(request, 
            section__section_id=section_id,
            asset__asset_id=asset_id)
                                               
    def dispatch_template_list(self, request, **kwargs):
        template_resource = StoryTemplateResource()
        return template_resource.dispatch_list(request)

    def dispatch_template_detail(self, request, **kwargs):
        template_id = kwargs.pop('template_id')
        template_resource = StoryTemplateResource()
        return template_resource.dispatch_detail(request, template_id=template_id)

    def dispatch_container_template_list(self, request, **kwargs):
        resource = ContainerTemplateResource()
        return resource.dispatch_list(request, **kwargs)

    def dispatch_metadata_list(self, request, resource, **kwargs):
        """
        Dispatcher for nested resources that allow setting/replacing 
        story metadata

        """
        try:
            base_bundle = self.build_bundle(request=request)
            story = self.cached_obj_get(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        return resource.dispatch_list(request, story_id=story.story_id)

    def dispatch_storycategory_list(self, request, **kwargs):
        return self.dispatch_metadata_list(request, StoryCategoryResource(), **kwargs)

    def dispatch_storyplace_list(self, request, **kwargs):
        return self.dispatch_metadata_list(request, StoryPlaceResource(), **kwargs)

    def dispatch_storyorganization_list(self, request, **kwargs):
        return self.dispatch_metadata_list(request, StoryOrganizationResource(), **kwargs)

    def dispatch_storyproject_list(self, request, **kwargs):
        return self.dispatch_metadata_list(request, StoryProjectResource(), **kwargs)

    def dispatch_storyrelation_list(self, request, **kwargs):
        return self.dispatch_metadata_list(request, StoryRelationResource(), **kwargs)

class SectionResource(TranslatedModelResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title')
    story = fields.ToOneField(StoryResource, 'story')

    layout = fields.CharField(attribute='layout')
    """layout_id of related ``SectionLayout`` object"""
    layout_template = fields.CharField(readonly=True)
    help = fields.CharField(attribute='help', null=True)
    template_section = fields.CharField(attribute='template_section',
        null=True)

    class Meta:
        always_return_data = True
        queryset = Section.objects.all().order_by('weight')
        resource_name = 'sections'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch', 'put', 'delete']
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

    def authorized_create_detail(self, object_list, bundle):
        try:
            return self._meta.authorization.obj_has_perms(bundle.obj.story, 
                    bundle.request.user, ['change']) 
        except Unauthorized, e:
            self.unauthorized_result(e)

    def obj_create(self, bundle, **kwargs):
        story_id = kwargs.pop('story__story_id')
        kwargs['story'] = Story.objects.get(story_id=story_id)
        return super(SectionResource, self).obj_create(bundle, **kwargs)

    def dehydrate_layout(self, bundle):
        return bundle.obj.layout.layout_id

    def hydrate_layout(self, bundle):
        layout = bundle.data.get('layout')
        # HACK: This gets called twice, I'm thinking because I'm
        # converting a ForeignKey field to text and back again
        # Only update the bundle data if it hasn't already
        # been converted to a SectionLayout object
        if layout and layout.__class__ != SectionLayout:
            bundle.data['layout'] = SectionLayout.objects.get(layout_id__exact=layout)
        return bundle

    def dehydrate_layout_template(self, bundle):
        return bundle.obj.layout.get_template_contents()

    def dehydrate_help(self, bundle):
        if bundle.obj.help:
            return {
                'help_id': bundle.obj.help.help_id,
                'title': bundle.obj.help.title,
                'body': bundle.obj.help.body,
            }
        else:
            return None

    def hydrate_help(self, bundle):
        help = bundle.data.get('help', None)
        if help and not isinstance(help, Help):
            bundle.data['help'] = Help.objects.get(help_id=help['help_id'])
        return bundle

    def dehydrate_template_section(self, bundle):
        if bundle.obj.template_section:
            return bundle.obj.template_section.section_id
        else:
            return None

    def hydrate_template_section(self, bundle):
        template_section = bundle.data.get('template_section', None)
        if template_section and not isinstance(template_section, Section):
            bundle.data['template_section'] = Section.objects.get(section_id=template_section)
        return bundle


class SectionAssetResource(HookedModelResource):
    asset = fields.ToOneField(AssetResource, 'asset', full=True)
    container = fields.CharField(attribute='container')

    class Meta:
        queryset = SectionAsset.objects.all()
        resource_name = 'sectionassets'
        detail_allowed_methods = ['get', 'post', 'delete']
        list_allowed_methods = ['get', 'post']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        # Hide the underlying id
        excludes = ['id']

        # Custom meta attributes
        parent_resource = StoryResource

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            obj = bundle_or_obj.obj 
        else:
            obj = bundle_or_obj

        kwargs['asset_id'] = obj.asset.asset_id
        kwargs['section_id'] = obj.section.section_id
        kwargs['story_id'] = obj.section.story.story_id

        return kwargs

    def resource_uri_kwargs(self, bundle_or_obj=None):
        """
        Builds a dictionary of kwargs to help generate URIs.

        This retrieves the resource_name and api_name from the parent resource
        as this resource is designed to be nested under ``StoryResource``

        """
        kwargs = super(SectionAssetResource, self).resource_uri_kwargs(bundle_or_obj)
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

    def dehydrate_container(self, bundle):
        return bundle.obj.container.name

    def hydrate_container(self, bundle):
        bundle.data['container'] = Container.objects.get(name=bundle.data['container'])
        return bundle

    def obj_create(self, bundle, **kwargs):
        section_id = kwargs.pop('section__section_id')
        kwargs['section'] = Section.objects.get(section_id=section_id)
        try:
            return super(SectionAssetResource, self).obj_create(bundle, **kwargs)
        except IntegrityError:
            # An asset is already assigned to this section/
            # container
            
            # Roll back the transaction
            transaction.rollback_unless_managed()
            logger.warn("Attempted duplicate assignment of asset %s to "
                        "section %s in container %s" % 
                        (bundle.obj.asset.asset_id, 
                         bundle.obj.section.section_id, 
                         bundle.obj.container.name))
            msg = ("An asset has already been assigned to this section and "
                    "container")
            raise ImmediateHttpResponse(response=http.HttpBadRequest(msg))

    def apply_request_kwargs(self, obj_list, bundle, **kwargs):
        section_id = kwargs.get('section__section_id')
        if section_id:
            return obj_list.filter(section__section_id=section_id)
        else:
            return obj_list


class StoryTemplateResource(TranslatedModelResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title')
    description = fields.CharField(attribute='description')
    tag_line = fields.CharField(attribute='tag_line')
    story = fields.ToOneField(StoryResource, attribute='story', 
                               blank=True, null=True)
    ingredients = fields.CharField(attribute='ingredients', blank=True,
                                   null=True)
    best_for = fields.CharField(attribute='best_for', blank=True, null=True)
    tip = fields.CharField(attribute='tip', blank=True, null=True)
    examples = fields.ListField(blank=True, null=True)
    
    class Meta:
        queryset = StoryTemplate.objects.all()
        resource_name = 'templates'
        allowed_methods = ['get']
        # Hide the underlying id
        excludes = ['id']
        authentication = Authentication()
        authorization = LoggedInAuthorization()

        # Custom meta attributes
        # Class of the resource under which this is nested
        parent_resource = StoryResource

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

        kwargs['template_id'] = obj.template_id

        return kwargs

    def resource_uri_kwargs(self, bundle_or_obj=None):
        """
        Builds a dictionary of kwargs to help generate URIs.

        This retrieves the resource_name and api_name from the parent resource
        as this resource is designed to be nested under ``StoryResource``

        """
        kwargs = super(StoryTemplateResource, self).resource_uri_kwargs(bundle_or_obj)
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

    def dehydrate_examples(self, bundle):
        if bundle.obj.examples:
            return [{'title': story.title, 'url': story.get_absolute_url()}
                    for story in bundle.obj.examples.all()]
        else:
            return []


class PutListSubResource(HookedModelResource):
    """Base resource class for replacing a Story's related models from a list of ids"""
    class Meta:
        list_allowed_methods = ['put']
        authentication = Authentication()
        authorization = LoggedInAuthorization()

        # Custom meta attributes
        parent_resource = StoryResource
        related_id_name = 'pk'
        related_queryset = None

    def resource_uri_kwargs(self, bundle_or_obj=None):
        """
        Builds a dictionary of kwargs to help generate URIs.

        This retrieves the resource_name and api_name from the parent resource
        as this resource is designed to be nested under ``StoryResource``

        """
        kwargs = super(PutListSubResource, self).resource_uri_kwargs(bundle_or_obj)
        kwargs['resource_name'] = self._meta.parent_resource._meta.resource_name 
        if self._meta.parent_resource._meta.api_name is not None:
            kwargs['api_name'] = self._meta.parent_resource._meta.api_name
        return kwargs

    def alter_hydrated_object_list(self, request, object_list):
        """Hook to limit the list of objects that will be associated with the story"""
        return object_list

    def authorized_update_related_obj(self, request, related_obj):
        try:
            return self._meta.authorization.obj_has_perms(related_obj, 
                    request.user, ['change']) 
        except Unauthorized, e:
            self.unauthorized_result(e)

    def put_list(self, request, **kwargs):
        story_id = kwargs.pop('story_id')
        obj = Story.objects.get(story_id=story_id)
        self.authorized_update_related_obj(request=request, related_obj=obj)

        related_ids = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        related_ids = self.alter_deserialized_list_data(request, related_ids)
        filter_kwargs = {}
        filter_kwargs[self._meta.related_id_name + "__in"] = related_ids
        related_objects = self._meta.related_queryset.filter(**filter_kwargs)
        related_objects = self.alter_hydrated_object_list(request, 
            related_objects) 

        if len(related_objects) != len(related_ids):
            raise BadRequest("Invalid IDs")
        related_manager = getattr(obj, self._meta.related_attr)
        related_manager.clear()
        related_manager.add(*list(related_objects))
        obj.save()


class StoryCategoryResource(PutListSubResource):
    class Meta(PutListSubResource.Meta):
        resource_name = 'storycategories'

        # Custom meta attributes
        related_attr = 'topics'
        related_queryset = Category.objects.all()


class StoryPlaceResource(PutListSubResource):
    class Meta(PutListSubResource.Meta):
        resource_name = 'storyplaces'

        # Custom meta attributes
        related_attr = 'places'
        related_queryset = Place.objects.all()
        related_id_name = 'place_id'


class StoryOrganizationResource(PutListSubResource):
    class Meta(PutListSubResource.Meta):
        resource_name = 'storyorganizations'

        # Custom meta attributes
        related_attr = 'organizations'
        related_queryset = Organization.objects.published()
        related_id_name = 'organization_id'

    def alter_hydrated_object_list(self, request, object_list):
        for obj in object_list:
            if obj not in request.user.organizations.all():
                raise BadRequest("User is not a member of organization with id %s" % obj.organization_id)
        return object_list

class StoryProjectResource(PutListSubResource):
    class Meta(PutListSubResource.Meta):
        resource_name = 'storyprojects'

        # Custom meta attributes
        related_attr = 'projects'
        related_queryset = Project.objects.published()
        related_id_name = 'project_id'

    def alter_hydrated_object_list(self, request, object_list):
        for obj in object_list:
            if obj not in request.user.projects.all():
                raise BadRequest("User is not a member of project with id %s" % obj.project_id)
        return object_list


class StoryRelationResource(HookedModelResource):
    source = fields.CharField(attribute='source')
    target = fields.CharField(attribute='target')

    class Meta:
        always_return_data = True
        queryset = StoryRelation.objects.all()
        resource_name = 'related'
        list_allowed_methods = ['get', 'post', 'put']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        # Hide the underlying id
        excludes = ['id']

    def apply_request_kwargs(self, obj_list, bundle, **kwargs):
        story_id = kwargs.get('story_id')
        if story_id:
            q = Q(source__story_id=story_id)
            q = q | Q(target__story_id=story_id)
            return obj_list.filter(q)
        else:
            return obj_list

    def obj_delete_list(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete_list``.

        Takes optional ``kwargs``, which can be used to narrow the query.
        """
        story_id = kwargs.pop('story_id')
        if story_id:
            q = Q(source__story_id=story_id)
            q = q | Q(target__story_id=story_id)
            q = q & Q(**kwargs)

        objects_to_delete = self.obj_get_list(bundle=bundle, **kwargs).filter(q)
        deletable_objects = self.authorized_delete_list(objects_to_delete, bundle)

        if hasattr(deletable_objects, 'delete'):
            # It's likely a ``QuerySet``. Call ``.delete()`` for efficiency.
            deletable_objects.delete()
        else:
            for authed_obj in deletable_objects:
                authed_obj.delete()

    def put_list(self, request, **kwargs):
        """
        Replaces a collection of resources with another collection.

        Unlike the default put_list, this doesn't expect the new collections
        to be wrapped in an 'objects' property.
        """
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)

        basic_bundle = self.build_bundle(request=request)
        self.obj_delete_list_for_update(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        bundles_seen = []

        for object_data in deserialized:
            bundle = self.build_bundle(data=dict_strip_unicode_keys(object_data), request=request)

            # Attempt to be transactional, deleting any previously created
            # objects if validation fails.
            try:
                self.obj_create(bundle, request=request, **self.remove_api_resource_names(kwargs))
                bundles_seen.append(bundle)
            except ImmediateHttpResponse:
                self.rollback(bundles_seen)
                raise

        if not self._meta.always_return_data:
            return http.HttpNoContent()
        else:
            to_be_serialized = {}
            to_be_serialized[self._meta.collection_name] = [self.full_dehydrate(bundle) for bundle in bundles_seen]
            to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
            return self.create_response(request, to_be_serialized, response_class=http.HttpAccepted)

    def dehydrate_source(self, bundle):
        if bundle.obj.source:
            return bundle.obj.source.story_id
        else:
            return None

    def hydrate_source(self, bundle):
        source = bundle.data.get('source', None)
        if source and not isinstance(source, Story):
            bundle.data['source'] = Story.objects.get(story_id=source)
        return bundle

    def dehydrate_target(self, bundle):
        if bundle.obj.target:
            return bundle.obj.target.story_id
        else:
            return None

    def hydrate_target(self, bundle):
        target = bundle.data.get('target', None)
        if target and not isinstance(target, Story):
            bundle.data['target'] = Story.objects.get(story_id=target)
        return bundle


class ContainerTemplateResource(HookedModelResource):
    # Define foreign key fields
    container = fields.CharField(attribute='container')
    template = fields.CharField(attribute='template')
    section = fields.CharField(attribute='section')
    help = fields.CharField(attribute='help', blank=True, null=True)

    class Meta:
        always_return_data = True
        queryset = ContainerTemplate.objects.all()
        resource_name = 'containertemplates'
        list_allowed_methods = ['get']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        # Hide the underlying id
        excludes = ['id']

    def dehydrate_container(self, bundle):
        return bundle.obj.container.name

    def dehydrate_help(self, bundle):
        if bundle.obj.help:
            return {
                'help_id': bundle.obj.help.help_id,
                'title': bundle.obj.help.title,
                'body': bundle.obj.help.body,
            }
        else:
            return None

    def dehydrate_section(self, bundle):
        return bundle.obj.section.section_id

    def dehydrate_template(self, bundle):
        return bundle.obj.template.template_id

    def apply_request_kwargs(self, obj_list, bundle, **kwargs):
        story_id = kwargs.get('story_id')
        template_id = kwargs.get('template_id')
        if story_id:
            template = StoryTemplate.objects.get(story__story_id=story_id)
            return obj_list.filter(template=template)
        elif template_id:
            return obj_list.filter(template__template_id=template_id)
        else:
            return obj_list
