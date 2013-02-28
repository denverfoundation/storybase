from django.views.generic import DetailView, ListView
from cmsplugin_storybase.models import NewsItem

class NewsItemDetailView(DetailView):
    """A single news item"""
    model = NewsItem

class NewsItemListView(ListView):
    """List of all news items"""
    queryset = NewsItem.objects.published().order_by('-published')
    paginate_by = 10

    def get_queryset(self):
        qs = super(NewsItemListView, self).get_queryset()
        if 'year' in self.kwargs:
            qs = qs.filter(published__year=self.kwargs['year'])
        if 'month' in self.kwargs:
            qs = qs.filter(published__month=self.kwargs['month'])
        return qs

