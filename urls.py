from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from ajax_select import urls as ajax_select_urls

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'atlas.views.home', name='home'),
    # url(r'^atlas/', include('atlas.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),

    # 3rd-party apps
    (r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^accounts/', include('allauth.urls')),

    # StoryBase URLs
    (r'^s/user/', include('storybase_user.urls')),
    (r'^s/place/', include('storybase_place.urls')),
    (r'^s/', include('storybase_story.urls')),

    # django CMS URLs
    url(r'^', include('cms.urls')),

)

if settings.DEBUG:
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),
) + urlpatterns
