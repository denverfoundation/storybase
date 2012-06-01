from geopy import geocoders

from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS 
from tastypie.resources import Resource, ModelResource
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization

from storybase_geo.models import GeoLevel, Place

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
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng =lng

class GeocoderResource(Resource):
    lat = fields.FloatField(attribute='lat')
    lng = fields.FloatField(attribute='lng')

    class Meta:
        resource_name = 'geocode'
        allowed_methods = ['get']
        detail_allowed_methods = []
        include_resource_uri = False
	# Allow open access to this resource for now since it's read-only
        authentication = Authentication()
        authorization = ReadOnlyAuthorization()

    def obj_get_list(self, request=None, **kwargs):
        results = []
        geocoder = geocoders.GeocoderDotUS()
        address = request.GET.get('q', None)
        if address:
            response = geocoder.geocode(address)
            if response:
                place, (lat, lng) = response
                result = {
                  'lat': float(lat),
                  'lng': float(lng)
                }
                result = GeocodeObject(lat=float(lat), lng=float(lng))
                results.append(result)

        return results 
