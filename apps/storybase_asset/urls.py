"""URL routing definitions"""

from django.conf import settings
from django.conf.urls import patterns, url

from storybase_asset.views import AssetDetailView, DataSetDetailView, AssetContentView

uuid_pattern = settings.UUID_PATTERN

urlpatterns = patterns('',
    url(r'^assets/(?P<asset_id>{})/content$'.format(uuid_pattern),
        AssetContentView.as_view(), name='asset_content_view'), 
    url(r'^assets/(?P<asset_id>{})/$'.format(uuid_pattern),
        AssetDetailView.as_view(), name='asset_detail'), 
    url(r'^datasets/(?P<dataset_id>{})/$'.format(uuid_pattern),
        DataSetDetailView.as_view(), name='dataset_detail'),
  
)
