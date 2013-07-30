from django.conf.urls.defaults import patterns, url

from storybase_messaging.views import (SiteContactMessageCreateView,
    StoryNotificationDetailView)

urlpatterns = patterns('',
    url(r'^contact/$',
        SiteContactMessageCreateView.as_view(), name='contact'), 
    url(r'^notifications/(?P<pk>[0-9]+)/$',
        StoryNotificationDetailView.as_view(), name='storynotification_detail'),
)
