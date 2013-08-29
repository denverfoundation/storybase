from django.conf.urls.defaults import patterns, url 

from storybase_taxonomy.views import CategoryExplorerRedirectView, TagStoryListView

urlpatterns = patterns('',
    url(r'topics/(?P<slug>[0-9a-z-]+)/$',
        CategoryExplorerRedirectView.as_view(),
        name='topic_stories'),
    url(r'tags/(?P<slug>[0-9a-z-]+)/$',
        TagStoryListView.as_view(),
        name='tag_stories'),
)
