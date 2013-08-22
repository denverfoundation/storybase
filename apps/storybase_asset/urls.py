"""URL routing definitions"""

from django.conf.urls import patterns, url

from storybase_asset.views import AssetDetailView, DataSetDetailView, AssetContentView

urlpatterns = patterns('',
    url(r'assets/(?P<asset_id>[0-9a-f]{32,32})/content$',
	AssetContentView.as_view(), name='asset_content_view'), 
    url(r'assets/(?P<asset_id>[0-9a-f]{32,32})/$', AssetDetailView.as_view(),
	name='asset_detail'), 
    url(r'datasets/(?P<dataset_id>[0-9a-f]{32,32})/$',
	DataSetDetailView.as_view(), name='dataset_detail'),
  
)
