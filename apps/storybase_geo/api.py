from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS 
from tastypie.resources import Resource, ModelResource
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization

from storybase_geo import settings
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
        def import_class(import_path):
            path_parts = import_path.split('.')
            class_name = path_parts[-1]
            module_name = '.'.join(path_parts[:-1])
            module = __import__(module_name, globals(), locals(), [class_name],
                                -1)
            return getattr(module, class_name)

        geocoder_class = import_class(settings.STORYBASE_GEOCODER)
        return geocoder_class(**settings.STORYBASE_GEOCODER_ARGS)
        
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
