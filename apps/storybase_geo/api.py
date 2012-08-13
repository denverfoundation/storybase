from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist

from tastypie import fields, http
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS 
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.resources import Resource, ModelResource
from tastypie.utils import trailing_slash

from storybase.api import DelayedAuthorizationResource, LoggedInAuthorization
from storybase_geo import settings
from storybase_geo.models import GeoLevel, Location, Place
from storybase_geo.utils import get_geocoder
from storybase_story.models import Story

class GeoLevelResource(ModelResource):
    parent_id = fields.IntegerField(attribute='parent__id', blank=True, null=True)
    class Meta:
        queryset = GeoLevel.objects.all()
        resource_name = 'geolevels'
        allowed_methods = ['get']
	    # Allow open access to this resource for now since it's read-only
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        fields = ['id', 'name', 'parent_id']
        filtering = {
            'id': ('exact',),
            'name': ALL
        }


class LocationResource(DelayedAuthorizationResource):
    class Meta:
        always_return_data = True
        queryset = Location.objects.all()
        resource_name = 'locations'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        detail_uri_name = 'location_id'
        # Hide the underlying id
        excludes = ['id', 'point']

        # Custom
        delayed_authorization_methods = ['delete_detail']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
        ]

    def apply_request_kwargs(self, obj_list, request=None, **kwargs):
        filters = {}
        story_id = kwargs.get('story_id')
        if story_id:
            filters['stories__story_id'] = story_id

        new_obj_list = obj_list.filter(**filters)

        return new_obj_list

    def obj_create(self, bundle, request=None, **kwargs):
        story_id = kwargs.get('story_id')
        if story_id:
            try:
                story = Story.objects.get(story_id=story_id) 
                if not story.has_perm(request.user, 'change'):
                    raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to change the story matching the provided story ID"))
            except ObjectDoesNotExist:
                raise ImmediateHttpResponse(response=http.HttpNotFound("A story matching the provided story ID could not be found"))

        # Set the asset's owner to the request's user
        if request.user:
            kwargs['owner'] = request.user

        # Let the superclass create the object
        bundle = super(LocationResource, self).obj_create(
            bundle, request, **kwargs)

        if story_id:
            # Associate the newly created object with the story
            story.locations.add(bundle.obj)
            story.save()

        return bundle
        
    # BOOKMARK


class PlaceResource(ModelResource):
    geolevel = fields.ToOneField(GeoLevelResource, 'geolevel')

    class Meta:
        queryset = Place.objects.all()
        resource_name = 'places'
        allowed_methods = ['get']
	    # Allow open access to this resource for now since it's read-only
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()
        # Hide the underlying id
        excludes = ['id']
        filtering = {
            'geolevel': ALL_WITH_RELATIONS,
            'name': ALL,
        }

# TODO: Document, error handling
class GeocodeObject(object):
    def __init__(self, place, lat, lng):
        self.place = place
        self.lat = lat
        self.lng =lng

    def __unicode__(self):
        return "%s (%f, %f)" % (self.place, self.lng, self.lat)

    def __str__(self):
        return self.__unicode__()

class GeocoderResource(Resource):
    """
    Proxy for geocoding as most geocoders don't support JSONP
   
    This simply wraps a geopy geocoder object.
    """
    lat = fields.FloatField(attribute='lat')
    lng = fields.FloatField(attribute='lng')
    place = fields.CharField(attribute='place')

    class Meta:
        resource_name = 'geocode'
        allowed_methods = ['get']
        detail_allowed_methods = []
        include_resource_uri = False
	# Allow open access to this resource for now since it's read-only
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()

    def get_geocoder(self):
        return get_geocoder()
        
    def obj_get_list(self, request=None, **kwargs):
        results = []
        geocoder = self.get_geocoder()
        address = request.GET.get('q', None)
        if address:
            geocoding_kwargs = {
                'exactly_one': settings.STORYBASE_GEOCODE_EXACTLY_ONE
            }
            try:
                for place, (lat, lng) in geocoder.geocode(address, **geocoding_kwargs):
                    result = GeocodeObject(place=place, lat=float(lat), lng=float(lng))
                    results.append(result)
            except ValueError:
                # No match for address found, results list will be empty
                pass

        return results 
