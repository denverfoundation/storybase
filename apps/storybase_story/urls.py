"""URL routing for storybase_story app"""

#import datetime
from django.conf import settings
from django.conf.urls.defaults import patterns, url
#from haystack.query import SearchQuerySet
#from haystack.views import FacetedSearchView

#from storybase_story.forms import StoryFacetedSearchForm
from storybase_story.views import (ExploreStoriesView, 
    StoryBuilderView, StoryDetailView, StoryViewerView, StoryUpdateView)

#sqs = SearchQuerySet().date_facet('pub_date', 
#                                   start_date=datetime.date(2009, 1, 1),
#                                   end_date=datetime.date.today(),
#                                   gap_by='month').facet('author') \
#                      .facet('school').facet('topic')

urlpatterns = patterns('',
#    url(r'search/', FacetedSearchView(form_class=StoryFacetedSearchForm,
#                                      searchqueryset=sqs),
#        name='story_search'),
    url(r'^build/$', StoryBuilderView.as_view(), name='story_builder'),
    url(r'^build/(?P<story_id>[0-9a-f]{32,32})/$', StoryBuilderView.as_view(), name='story_builder'),
    url(r'^build/(?P<story_id>[0-9a-f]{32,32})/(?P<step>data|tag|review|publish)/$', StoryBuilderView.as_view(), name='story_builder'),
    url(r'^explore/$', ExploreStoriesView.as_view(), name='explore_stories'),
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/$',
        StoryDetailView.as_view(), name='story_detail_by_id'), 
    url(r'^stories/(?P<slug>[0-9a-z-]+)/$',
        StoryDetailView.as_view(), name='story_detail'), 
    url(r'^stories/(?P<story_id>[0-9a-f]{32,32})/viewer/$',
        StoryViewerView.as_view(), name='story_viewer_by_id'), 
    url(r'^stories/(?P<slug>[0-9a-z-]+)/viewer/$',
        StoryViewerView.as_view(), name='story_viewer'), 
    url(r'^stories/(?P<slug>[0-9a-z-]+)/unpublish/$',  
        StoryUpdateView.as_view(), {'status': 'draft'}, name='story_unpublish'), 
    url(r'^stories/(?P<slug>[0-9a-z-]+)/publish/$',  
        StoryUpdateView.as_view(), {'status': 'published'}, name='story_publish'),
    url(r'^stories/(?P<slug>[0-9a-z-]+)/delete/$',  
        StoryUpdateView.as_view(), {'status': 'deleted'}, name='story_delete'),
    url(r'stories/(?P<source_story_id>[0-9a-f]{32,32})/build-connected/$', StoryBuilderView.as_view(), {'template': settings.STORYBASE_CONNECTED_STORY_TEMPLATE}, name='connected_story_builder'),
    url(r'stories/(?P<source_slug>[0-9a-z-]+)/build-connected/$', StoryBuilderView.as_view(), {'template': settings.STORYBASE_CONNECTED_STORY_TEMPLATE}, name='connected_story_builder'),
    url(r'stories/(?P<source_story_id>[0-9a-f]{32,32})/build-connected/(?P<story_id>[0-9a-f]{32,32})/$', StoryBuilderView.as_view(), {'template': settings.STORYBASE_CONNECTED_STORY_TEMPLATE}, name='connected_story_builder'),
    url(r'stories/(?P<source_slug>[0-9a-z-]+)/build-connected/(?P<story_id>[0-9a-f]{32,32})/$', StoryBuilderView.as_view(), {'template': settings.STORYBASE_CONNECTED_STORY_TEMPLATE}, name='connected_story_builder'),
)
