"""URL routing for storybase_story app"""

from django.conf import settings
from django.conf.urls import patterns, url

from storybase_story.feeds import StoriesFeed, TopicStoriesFeed
from storybase_story.views import (ExploreStoriesView, 
    StoryBuilderView, StoryDetailView, StoryViewerView,
    StoryUpdateView, StoryShareView, StorySharePopupView,
    StoryEmbedView, StoryEmbedPopupView)

urlpatterns = patterns('',
    url(r'^build/$', StoryBuilderView.as_view(), name='story_builder'),
    url(r'^build/(?P<story_id>[0-9a-f]{32,32})/$',
        StoryBuilderView.as_view(), name='story_builder'),
    url(r'^build/(?P<story_id>[0-9a-f]{32,32})/(?P<step>data|tag|info|publish)/$',
        StoryBuilderView.as_view(), name='story_builder'),
    url(r'^explore/$', ExploreStoriesView.as_view(), name='explore_stories'),
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/$',
        StoryDetailView.as_view(), name='story_detail_by_id'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/$',
        StoryDetailView.as_view(), name='story_detail'),
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/viewer/$',
        StoryViewerView.as_view(), name='story_viewer_by_id'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/viewer/$',
        StoryViewerView.as_view(), name='story_viewer'),
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/preview/$',
        StoryViewerView.as_view(), kwargs={'preview': True},
        name='story_viewer_preview'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/preview/$',
        StoryViewerView.as_view(), kwargs={'preview': True},
        name='story_viewer_preview'),
    url(r'stories/(?P<source_story_id>[0-9a-f]{32,32})/build-connected/$',
        StoryBuilderView.as_view(),
        {'template': settings.STORYBASE_CONNECTED_STORY_TEMPLATE},
        name='connected_story_builder'),
    url(r'stories/(?P<source_slug>[0-9a-z-]+)/build-connected/$',
        StoryBuilderView.as_view(),
        {'template': settings.STORYBASE_CONNECTED_STORY_TEMPLATE},
        name='connected_story_builder'),
    url(r'stories/(?P<source_story_id>[0-9a-f]{32,32})/build-connected/(?P<story_id>[0-9a-f]{32,32})/$',
        StoryBuilderView.as_view(),
        {'template': settings.STORYBASE_CONNECTED_STORY_TEMPLATE},
        name='connected_story_builder'),
    url(r'stories/(?P<source_slug>[0-9a-z-]+)/build-connected/(?P<story_id>[0-9a-f]{32,32})/$',
        StoryBuilderView.as_view(),
        {'template': settings.STORYBASE_CONNECTED_STORY_TEMPLATE},
        name='connected_story_builder'),
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/share/$',
        StoryShareView.as_view(), name='story_share'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/share/$',
        StoryShareView.as_view(), name='story_share'),
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/share/popup/$',
        StorySharePopupView.as_view(), name='story_share_popup'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/share/popup/$',
        StorySharePopupView.as_view(), name='story_share_popup'),
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/embed/$',
        StoryEmbedView.as_view(), name='story_embed'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/embed/$',
        StoryEmbedView.as_view(), name='story_embed'),
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/embed/popup/$',
        StoryEmbedPopupView.as_view(), name='story_embed_popup'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/embed/popup/$',
        StoryEmbedPopupView.as_view(), name='story_embed_popup'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/unpublish/$',  
        StoryUpdateView.as_view(), {'status': 'draft'}, 
        name='story_unpublish'), 
    url(r'^stories/(?P<slug>[0-9a-z-]+)/publish/$',  
        StoryUpdateView.as_view(), {'status': 'published'}, 
        name='story_publish'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/delete/$',  
        StoryUpdateView.as_view(), {'status': 'deleted'}, 
        name='story_delete'),
    url(r'^feeds/stories/$',
        StoriesFeed(), name='story_feed'),
    url(r'^feeds/topics/(?P<slug>[0-9a-z-]+)/$',
        TopicStoriesFeed(), name='topic_story_feed'),
)
