from haystack.indexes import (SearchIndex, CharField, FacetCharField, 
    FacetDateTimeField, FacetMultiValueField)
from haystack import site

from models import Story

class StoryIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = FacetCharField(model_attr='author')
    pub_date = FacetDateTimeField(model_attr='pub_date')
    # TODO: Use a meta class to dynamically populate these from "official"
    # tag sets 
    school = FacetMultiValueField()
    neighborhood = FacetMultiValueField()
    topic = FacetMultiValueField()
    organization = FacetMultiValueField()
    project = FacetMultiValueField()

    def _prepare_tag_set(self, obj, set_name):
        return [tag.name for tag in obj.tags.filter(tag_set__name=set_name)]

    def prepare_school(self, obj):
        return self._prepare_tag_set(obj, 'School')

    def prepare_neighborhood(self, obj):
        return self._prepare_tag_set(obj, 'Neighborhood')

    def prepare_topic(self, obj):
        return self._prepare_tag_set(obj, 'Topic')

    def prepare_organization(self, obj):
        return self._prepare_tag_set(obj, 'Organization')

    def prepare_project(self, obj):
        return self._prepare_tag_set(obj, 'Project')

    def index_queryset(self):
        return Story.objects.filter(status__exact='published')

site.register(Story, StoryIndex)
