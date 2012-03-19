from django.views.generic import DetailView
from models import Story

class StoryDetailView(DetailView):
    context_object_name = "story"
    queryset = Story.objects.all()

    def get_object(self):
        object = self.queryset.get(story_id=self.kwargs['story_id'])
        return object

    """
    def get_context_data(self, **kwargs):
        context = super(StoryDetailView, self).get_context_data(**kwargs)
        return context
    """
