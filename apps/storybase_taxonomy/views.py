from storybase_story.views import ExplorerRedirectView, StoryListView
from storybase_taxonomy.models import Category, Tag


class CategoryExplorerRedirectView(ExplorerRedirectView):
    def get_query_string(self, **kwargs):
        slug = kwargs.get('slug', None)
        if not slug:
            return None
        try:
            category = Category.objects.get(categorytranslation__slug=slug)
            return "topics=%d" % category.pk
        except Category.DoesNotExist:
            return None


class TagStoryListView(StoryListView):
    queryset = Tag.objects.all()
    related_field_name = 'tags'
