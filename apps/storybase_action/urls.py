"""URL routing for actions app"""

from django.conf.urls.defaults import patterns, url

from storybase_action.views import SiteContactMessageCreateView

urlpatterns = patterns('',
    url(r'contact/$',
        SiteContactMessageCreateView.as_view(), name='contact'), 
)
