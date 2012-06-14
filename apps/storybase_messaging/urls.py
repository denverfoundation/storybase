from django.conf.urls.defaults import patterns, url

from storybase_messaging.views import SiteContactMessageCreateView

print "GOT HERE"

urlpatterns = patterns('',
    url(r'^contact/$',
        SiteContactMessageCreateView.as_view(), name='contact'), 
)
