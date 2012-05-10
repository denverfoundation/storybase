from haystack.indexes import (RealTimeSearchIndex, CharField, FacetCharField, 
    FacetDateTimeField, FacetMultiValueField)
from haystack import site

from models import Story

class StoryIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    author = FacetCharField(model_attr='author')
    published = FacetDateTimeField(model_attr='published')
    # TODO: Use a meta class to dynamically populate these from "official"
    # tag sets 
    topics = FacetMultiValueField()
    organizations = FacetMultiValueField()
    projects = FacetMultiValueField()

    def prepare_topics(self, obj):
        return [topic.name for topic in obj.topics.all()]

    def prepare_organizations(self, obj):
        return [organization.name for organization in obj.organizations.all()]

    def prepare_projects(self, obj):
	return [project.name for project in obj.projects.all()]

    def index_queryset(self):
        return Story.objects.filter(status__exact='published')

site.register(Story, StoryIndex)
