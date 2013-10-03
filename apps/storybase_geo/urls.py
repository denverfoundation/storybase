from django.conf.urls import patterns, url

from storybase_geo.views import PlaceExplorerRedirectView

urlpatterns = patterns('',
    url(r'places/(?P<slug>[0-9a-z-]+)/$',
        PlaceExplorerRedirectView.as_view(),
        name='place_stories'),
)
