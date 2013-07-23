from django.conf.urls.defaults import handler500, patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.decorators.cache import cache_page

from tastypie.api import Api

from storybase.api import CreativeCommonsLicenseGetProxyView
from storybase.views import JSErrorHandlerView
from storybase_asset.urls import urlpatterns as asset_urlpatterns
from storybase_help.urls import urlpatterns as help_urlpatterns
from storybase_user.urls import urlpatterns as user_urlpatterns
from storybase_story.urls import urlpatterns as story_urlpatterns
from storybase_asset.api import AssetResource, DataSetResource
from storybase_geo.api import (GeocoderResource, GeoLevelResource,
                               LocationResource, PlaceResource)
from storybase_help.api import (HelpResource)
from storybase_story.api import StoryResource
from storybase_taxonomy.api import TagResource

# Override default error handler with one that uses RequestContext
handler500 = 'storybase.views.defaults.server_error'

admin.autodiscover()

urlpatterns = patterns('')

# Set up Tastypie API resources
v0_1_api = Api(api_name='0.1')
v0_1_api.register(AssetResource())
v0_1_api.register(DataSetResource())
v0_1_api.register(StoryResource())
v0_1_api.register(GeocoderResource())
v0_1_api.register(GeoLevelResource())
v0_1_api.register(LocationResource())
v0_1_api.register(PlaceResource())
v0_1_api.register(HelpResource())
v0_1_api.register(TagResource())
urlpatterns += patterns('', 
    # REST API
    (r'^api/', include(v0_1_api.urls)),
    # Proxy for Creative Commons endpoint
    # Cache responses for 24 hours
    url(r"^api/%s/license/get/" % v0_1_api.api_name,
        cache_page(CreativeCommonsLicenseGetProxyView.as_view(), 60 * 60 * 24),
        name="api_cc_license_get"),
)

# Include storybase_user URL patterns
# Use this pattern instead of include since we want to put the URLs
# at the top-level
urlpatterns += user_urlpatterns + story_urlpatterns + asset_urlpatterns + help_urlpatterns 

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'atlas.views.home', name='home'),
    # url(r'^atlas/', include('atlas.foo.urls')),

    # StoryBase account management
    # This needs to come before the admin URLs in order to use
    # the custom login form
    (r'^accounts/', include('storybase_user.account_urls')),

    (r'^messaging/', include('storybase_messaging.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),

    # Make translations available in JavaScript
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {}),

    # JS errors
    url(r'^errors/', JSErrorHandlerView.as_view(), name="js_error_log"), 

    # Comments
    (r'^comments/', include('django.contrib.comments.urls')),

    # Search via Haystack
    (r'^search/', include('search_urls')),

    # 3rd-party apps
    (r'^tinymce/', include('tinymce.urls')),
    (r'^accounts/', include('storybase_user.registration.backends.extrainfo.urls')),
    (r'^accounts/', include('social_auth.urls')),
    (r'^notices/', include('notification.urls')),

    # django CMS URLs
    url(r'^', include('cms.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
