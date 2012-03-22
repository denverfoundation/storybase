from django.conf.urls.defaults import patterns, url
from views import asset_detail, dataset_detail

urlpatterns = patterns('',
    url(r'assets/(?P<asset_id>[0-9a-f]{32,32})/$', asset_detail, name='asset_detail'), 
    url(r'datasets/(?P<dataset_id>[0-9a-f]{32,32})/$', dataset_detail, name='dataset_detail'), 
)
