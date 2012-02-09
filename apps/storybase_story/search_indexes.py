from haystack.indexes import (SearchIndex, CharField, FacetCharField, 
    FacetMultiValueField)
from haystack import site

from models import Story

class StoryIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = FacetCharField(model_attr='author')
    # TODO: Use a meta class to dynamically populate these from "official"
    # tag sets 
    school = FacetMultiValueField()
    #neighborhood = FacetMultiValueField()
    topic = FacetMultiValueField()
    #organization = FacetMultiValueField()
    #project = FacetMultiValueField()

    def _prepare_tag_set(self, obj, set_name):
        return [tag.name for tag in obj.tags.filter(tag_set__name=set_name)]

    def prepare_school(self, obj):
        return self._prepare_tag_set(obj, 'School')

    def prepare_topic(self, obj):
        return self._prepare_tag_set(obj, 'Topic')

    def index_queryset(self):
        return Story.objects.filter(status__exact='published')

site.register(Story, StoryIndex)
