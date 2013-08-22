"""
URL configuration for list and detail views for news items

This is meant to be attached to ``NewsItemApphook`` 
"""
from django.conf.urls import patterns, url
from cmsplugin_storybase.views import NewsItemDetailView, NewsItemListView

urlpatterns = patterns('',
    url(r'^$', NewsItemListView.as_view(), name='latest_updates'),
    url(r'^(?P<year>\d{4})/$', NewsItemListView.as_view(), name='latest_updates'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', NewsItemListView.as_view(), name='latest_updates'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>[0-9a-z-]+)/$', NewsItemDetailView.as_view(), name='newsitem_detail'),
)
