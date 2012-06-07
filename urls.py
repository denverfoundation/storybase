from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

#from ajax_select import urls as ajax_select_urls
from tastypie.api import Api

from storybase_action.urls import urlpatterns as action_urlpatterns
from storybase_asset.urls import urlpatterns as asset_urlpatterns
from storybase_user.urls import urlpatterns as user_urlpatterns
from storybase_story.urls import urlpatterns as story_urlpatterns
from storybase_geo.api import (GeocoderResource, GeoLevelResource,
                               PlaceResource)
from storybase_story.api import StoryResource

admin.autodiscover()

urlpatterns = patterns('')

# Set up Tastypie API resources
v0_1_api = Api(api_name='0.1')
v0_1_api.register(StoryResource())
v0_1_api.register(GeocoderResource())
v0_1_api.register(GeoLevelResource())
v0_1_api.register(PlaceResource())
urlpatterns += patterns('', 
    # REST API
    (r'^api/', include(v0_1_api.urls)),
)

# Include storybase_user URL patterns
# Use this pattern instead of include since we want to put the URLs
# at the top-level
urlpatterns += action_urlpatterns + user_urlpatterns + story_urlpatterns + asset_urlpatterns 

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'atlas.views.home', name='home'),
    # url(r'^atlas/', include('atlas.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    

    # Make translations available in JavaScript
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {}),

    # 3rd-party apps
    (r'^tinymce/', include('tinymce.urls')),
    (r'^accounts/', include('storybase_user.registration.backends.extrainfo.urls')),
    (r'^accounts/', include('social_auth.urls')),

    # StoryBase account management
    (r'^accounts/', include('storybase_user.account_urls')),

    # django CMS URLs
    url(r'^', include('cms.urls')),

)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
