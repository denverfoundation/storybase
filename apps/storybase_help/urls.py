from django.conf.urls.defaults import *
from storybase_help.views import HelpDetailView
   
urlpatterns = patterns('',
    url(r'^help/(?P<help_id>[0-9a-f]{32,32})/$',
        HelpDetailView.as_view(), name='help_detail'),
    url(r'^help/(?P<slug>[0-9a-z-]+)/$',
        HelpDetailView.as_view(), name='help_detail'),
)
