import datetime
from django.conf.urls.defaults import *
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

from storybase_story.forms import StoryFacetedSearchForm
from views import StoryDetailView

sqs = SearchQuerySet().date_facet('pub_date', start_date=datetime.date(2009, 1, 1), end_date=datetime.date.today(), gap_by='month').facet('author').facet('school').facet('topic')

urlpatterns = patterns('',
    url(r'search/', FacetedSearchView(form_class=StoryFacetedSearchForm, searchqueryset=sqs),
        name='story_search'),
    url(r'stories/(?P<slug>\S+)/$', StoryDetailView.as_view(), name='story_detail'), 
)
