from django.conf.urls import handler500, patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic.base import RedirectView

from tastypie.api import Api

from storybase.api import CreativeCommonsLicenseGetProxyView
from storybase.views import JSErrorHandlerView
from storybase_asset.api import AssetResource, DataSetResource
from storybase_geo.api import (GeocoderResource, GeoLevelResource,
                               LocationResource, PlaceResource)
from storybase_help.api import (HelpResource)
from storybase_story.api import StoryResource
from storybase_taxonomy.api import TagResource
from storybase_badge.api import BadgeResource

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
v0_1_api.register(BadgeResource())

urlpatterns += patterns('',
    # REST API
    (r'^api/', include(v0_1_api.urls)),
    # Proxy for Creative Commons endpoint
    # Cache responses for 24 hours
    url(r"^api/%s/license/get/" % v0_1_api.api_name,
        cache_page(60 * 60 * 24)(CreativeCommonsLicenseGetProxyView.as_view()),
        name="api_cc_license_get"),
)

urlpatterns += i18n_patterns('',
    # Include storybase URL patterns
    (r'^', include('storybase_user.urls')),
    (r'^', include('storybase_story.urls')),
    (r'^', include('storybase_asset.urls')),
    (r'^', include('storybase_help.urls')),
    (r'^', include('storybase_taxonomy.urls')),
    (r'^', include('storybase_geo.urls')),
    (r'^', include('storybase_badge.urls')),

    # StoryBase account management
    # This needs to come before the admin URLs in order to use
    # the custom login form
    (r'^accounts/', include('storybase_user.account_urls')),
    (r'^messaging/', include('storybase_messaging.urls')),

    # Comments
    (r'^comments/', include('django_comments.urls')),

    # Search via Haystack
    (r'^search/', include('search_urls')),

    # 3rd-party apps
    (r'^accounts/', include('storybase_user.registration.backends.extrainfo.urls')),
    url(r'^accounts/', include('social.apps.django_app.urls', namespace='social')),
    (r'^notices/', include('notification.urls')),

    url(r'^$', RedirectView.as_view(url='/home/')),

    # django CMS URLs
    url(r'^', include('cms.urls')),

)


urlpatterns += patterns('',
    url(r'^', include('storybase_story.widget_urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Make translations available in JavaScript
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {}),

    # JS errors
    url(r'^errors/', JSErrorHandlerView.as_view(), name="js_error_log"),

    # 3rd-party apps
    (r'^tinymce/', include('tinymce.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'', include('django.contrib.staticfiles.urls')),
    )
