"""REST API for Stories"""

from django.conf.urls.defaults import url
from django.core.urlresolvers import NoReverseMatch

from haystack.query import SearchQuerySet
from haystack.utils.geo import D, Point

from tastypie import fields
from tastypie.bundle import Bundle
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization

from storybase.utils import get_language_name
from storybase_geo.models import Place
from storybase_story.models import Story
from storybase_taxonomy.models import Category
from storybase_user.models import Organization, Project

class StoryResource(ModelResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title')
    summary = fields.CharField(attribute='summary')
    url = fields.CharField(attribute='get_absolute_url')
    topics = fields.ListField(readonly=True)
    organizations = fields.ListField(readonly=True)
    projects = fields.ListField(readonly=True)
    languages = fields.ListField(readonly=True, attribute='languages')
    # A list of lat/lon values for related Location objects as well as
    # centroids of Place tags
    points = fields.ListField(readonly=True)

    class Meta:
        queryset = Story.objects.filter(status__exact='published')
        resource_name = 'stories'
        allowed_methods = ['get']
	    # Allow open access to this resource for now since it's read-only
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        # Hide the underlying id
        excludes = ['id']
        # Filter arguments for custom explore endpoint
        explore_filter_fields = ['topics', 'projects', 'organizations', 'languages', 'places']
        explore_point_field = 'points'

    def override_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/explore%s$'  % (self._meta.resource_name, trailing_slash()), self.wrap_view('explore_get_list'), name="api_explore_get_list"),
            url(r"^(?P<resource_name>%s)/(?P<story_id>[0-9a-f]{32,32})/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def get_resource_uri(self, bundle_or_obj):
        """
        Handles generating a resource URI for a single resource.

        Uses the model's ``story_id`` in order to create the URI.
        """
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.story_id
        else:
            kwargs['pk'] = bundle_or_obj.story_id

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

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
