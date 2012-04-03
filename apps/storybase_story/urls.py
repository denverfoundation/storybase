"""URL routing for storybase_story app"""

#import datetime
from django.conf.urls.defaults import patterns, url
#from haystack.query import SearchQuerySet
#from haystack.views import FacetedSearchView

#from storybase_story.forms import StoryFacetedSearchForm
#from views import StoryDetailView
from storybase_story.views import story_detail

#sqs = SearchQuerySet().date_facet('pub_date', 
#                                   start_date=datetime.date(2009, 1, 1),
#                                   end_date=datetime.date.today(),
#                                   gap_by='month').facet('author') \
#                      .facet('school').facet('topic')

urlpatterns = patterns('',
#    url(r'search/', FacetedSearchView(form_class=StoryFacetedSearchForm,
#                                      searchqueryset=sqs),
#        name='story_search'),

    url(r'stories/(?P<story_id>[0-9a-f]{32,32})/$', story_detail,
        name='story_detail'), 
# Use this if we decide not to go with our language-based routing scheme.
#    url(r'stories/(?P<story_id>[0-9a-f]{32,32})/$',
#         StoryDetailView.as_view(), name='story_detail'), 
)
