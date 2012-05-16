from django.utils import simplejson
from tastypie.bundle import Bundle
from tastypie.fields import ApiField
from tastypie.resources import ModelResource
from models import DenverNeighborhood

class DenverNeighborhoodResource(ModelResource):
    geometry = ApiField()

    class Meta:
        queryset = DenverNeighborhood.objects.all()
        excludes = ['neigspss', 'name', 'neigh_id', 'identifier']
        resource_name = 'neighborhood'

    def dehydrate_geometry(self, bundle):
        geometry = simplejson.loads(bundle.obj.geom.geojson)
        geometry['type'] = bundle.obj.geom.geom_type
        return geometry 

    def dehydrate(self, bundle):
        bundle.data['type'] = 'Feature'
        bundle.data['properties'] = dict()
        for key in ('shape_leng', 'shape_area', 'name_lc', 'acres', 'sqm'):
          bundle.data['properties'][key] = bundle.data[key]
          del(bundle.data[key])
        bundle.data['properties']['center'] = bundle.obj.geom.point_on_surface.coords
        del(bundle.data['geom'])
        return bundle
