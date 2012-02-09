from django.conf.urls.defaults import *
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

from storybase_story.forms import StoryFacetedSearchForm

sqs = SearchQuerySet().facet('author').facet('school').facet('topic')

urlpatterns = patterns('',
    url(r'search/', FacetedSearchView(form_class=StoryFacetedSearchForm, searchqueryset=sqs),
        name='story_search'),
    #url(r'search/', include('haystack.urls')),
)
