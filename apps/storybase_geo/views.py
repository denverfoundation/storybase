from storybase_story.views import ExplorerRedirectView, StoryListWidgetView
from storybase_geo.models import Place 


class PlaceExplorerRedirectView(ExplorerRedirectView):
    def get_query_string(self, **kwargs):
        slug = kwargs.get('slug', None)
        if not slug:
            return None
        try:
            place = Place.objects.get(slug=slug)
            return "places=%s" % place.place_id
        except Place.DoesNotExist:
            return None

class PlaceWidgetView(StoryListWidgetView):
    queryset = Place.objects.all()
    related_field_name = "places"
