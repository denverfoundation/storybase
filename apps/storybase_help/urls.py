from django.conf import settings
from django.conf.urls import patterns, url
from storybase_help.views import HelpDetailView
   
urlpatterns = patterns('',
    url(r'^help/(?P<help_id>{})/$'.format(settings.UUID_PATTERN),
        HelpDetailView.as_view(), name='help_detail'),
    url(r'^help/(?P<slug>[0-9a-z-]+)/$',
        HelpDetailView.as_view(), name='help_detail'),
)
