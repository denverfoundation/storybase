from django.conf.urls.defaults import patterns, url

from storybase_messaging.views import SiteContactMessageCreateView

urlpatterns = patterns('',
    url(r'^contact/$',
        SiteContactMessageCreateView.as_view(), name='contact'), 
)
