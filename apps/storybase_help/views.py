from storybase.views.generic import ModelIdDetailView
from storybase_help.models import Help

class HelpDetailView(ModelIdDetailView):
    queryset = Help.objects.all()
