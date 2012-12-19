from django.conf.urls.defaults import *
from haystack.forms import SearchForm
from storybase.search.views import StorybaseSearchView

urlpatterns = patterns('haystack.views',
    url(r'^$', StorybaseSearchView(
        form_class=SearchForm
    ), name='haystack_search'),
)
