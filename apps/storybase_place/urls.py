from django.conf.urls.defaults import *
from views import NeighborhoodMapView 

urlpatterns = patterns('',
    url(r'neighborhood/', NeighborhoodMapView.as_view(), name='neighborhood_map'),
)
