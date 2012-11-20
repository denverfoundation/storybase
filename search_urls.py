from django.conf.urls.defaults import *
from haystack.forms import SearchForm
from haystack.views import SearchView

urlpatterns = patterns('haystack.views',
    url(r'^$', SearchView(
        form_class=SearchForm
    ), name='haystack_search'),
)
