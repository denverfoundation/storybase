from django.conf.urls.defaults import *
from tastypie.api import Api
from api import DenverNeighborhoodResource
from views import NeighborhoodMapView 

v0_1_api = Api(api_name='v0.1')
v0_1_api.register(DenverNeighborhoodResource())

urlpatterns = patterns('',
    url(r'api/', include(v0_1_api.urls)),
    url(r'neighborhood/', NeighborhoodMapView.as_view(), name='neighborhood_map'),
)
