from django.views.generic import DetailView
from models import Story

class StoryDetailView(DetailView):
    context_object_name = "story"
    model = Story

    """
    def get_context_data(self, **kwargs):
        context = super(StoryDetailView, self).get_context_data(**kwargs)
        return context
    """
