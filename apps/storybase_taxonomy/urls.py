from django.conf.urls.defaults import patterns, url 

from storybase_taxonomy.views import CategoryExplorerRedirectView, CategoryWidgetView, TagStoryListView, TagWidgetView

urlpatterns = patterns('',
    url(r'topics/(?P<slug>[0-9a-z-]+)/$',
        CategoryExplorerRedirectView.as_view(),
        name='topic_stories'),
    url(r'topics/(?P<slug>[0-9a-z-]+)/widget/$',
        CategoryWidgetView.as_view(),
        name='topic_widget'),
    url(r'tags/(?P<slug>[0-9a-z-]+)/$',
        TagStoryListView.as_view(),
        name='tag_stories'),
    url(r'tags/(?P<slug>[0-9a-z-]+)/widget/$',
        TagWidgetView.as_view(),
        name='tag_widget'),
)
