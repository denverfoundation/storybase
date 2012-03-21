from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
#from ajax_select import urls as ajax_select_urls
from storybase_asset.urls import urlpatterns as asset_urlpatterns
from storybase_user.urls import urlpatterns as user_urlpatterns
from storybase_story.urls import urlpatterns as story_urlpatterns

admin.autodiscover()

urlpatterns = patterns('')

# Include storybase_user URL patterns
# Use this pattern instead of include since we want to put the URLs
# at the top-level
urlpatterns += user_urlpatterns + story_urlpatterns + asset_urlpatterns 

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'atlas.views.home', name='home'),
    # url(r'^atlas/', include('atlas.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),

    # 3rd-party apps
    #(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    #(r'^accounts/', include('allauth.urls')),

    # django CMS URLs
    url(r'^', include('cms.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
