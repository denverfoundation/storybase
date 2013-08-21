from django.conf.urls.defaults import patterns, url

from storybase_geo.views import PlaceExplorerRedirectView, PlaceWidgetView 

urlpatterns = patterns('',
    url(r'places/(?P<slug>[0-9a-z-]+)/$',
        PlaceExplorerRedirectView.as_view(),
        name='place_stories'),
    url(r'places/(?P<slug>[0-9a-z-]+)/widget/$',
        PlaceWidgetView.as_view(),
        name='place_widget'),
)
