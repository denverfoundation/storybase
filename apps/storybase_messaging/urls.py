from django.conf.urls import patterns, url

from storybase_messaging.views import (SiteContactMessageCreateView,
    StoryContactMessageCreateView, StoryNotificationDetailView)

urlpatterns = patterns('',
    url(r'^contact/$',
        SiteContactMessageCreateView.as_view(), name='contact'),
    url(r'^storycontact/$',
        StoryContactMessageCreateView.as_view(), name='story_contact'),
    url(r'^notifications/(?P<pk>[0-9]+)/$',
        StoryNotificationDetailView.as_view(), name='storynotification_detail'),
)
