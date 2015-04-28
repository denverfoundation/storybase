from django.conf.urls import patterns, url
from storybase_story.forms import StorySearchForm
from storybase.search.views import StorybaseSearchView

urlpatterns = patterns('haystack.views',
    url(r'^$', StorybaseSearchView(
        form_class=StorySearchForm
    ), name='haystack_search'),
)
