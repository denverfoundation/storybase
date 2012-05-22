from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS 
from tastypie.resources import ModelResource
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
