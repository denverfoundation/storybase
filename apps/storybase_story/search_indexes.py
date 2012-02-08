from haystack.indexes import SearchIndex, CharField
from haystack import site

from models import Story

class StoryIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='author')

    def index_queryset(self):
        return Story.objects.all()

site.register(Story, StoryIndex)
