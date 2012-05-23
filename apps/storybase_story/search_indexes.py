from haystack.indexes import (RealTimeSearchIndex, CharField, FacetCharField, 
    FacetDateTimeField, FacetMultiValueField)
from haystack import site

from models import Story

class StoryIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    author = FacetCharField(model_attr='author')
    published = FacetDateTimeField(model_attr='published')
    created = FacetDateTimeField(model_attr='created')
    last_edited = FacetDateTimeField(model_attr='last_edited')
    # TODO: Use a meta class to dynamically populate these from "official"
    # tag sets 
    topic_ids = FacetMultiValueField()
    organization_ids = FacetMultiValueField()
    project_ids = FacetMultiValueField()
    language_ids = FacetMultiValueField()

    def prepare_topic_ids(self, obj):
        return [topic.id for topic in obj.topics.all()]

    def prepare_organization_ids(self, obj):
        return [organization.organization_id for organization in obj.organizations.all()]

    def prepare_project_ids(self, obj):
        return [project.project_id for project in obj.projects.all()]

    def prepare_language_ids(self, obj):
        return obj.get_languages()

    def index_queryset(self):
        return Story.objects.filter(status__exact='published')

    def should_update(self, instance, **kwargs):
        """
        Determine if an object should be updated in the index.
        """
        should_update = True
        translation_set = getattr(instance, instance.translation_set)
        if translation_set.count() == 0:
            should_update = False
        return should_update
        
site.register(Story, StoryIndex)
