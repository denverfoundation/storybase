import logging

from django.db.models import signals

from haystack import indexes

from storybase_asset.models import HtmlAssetTranslation
from storybase_geo.models import Location
from storybase_story.models import (SectionAsset, SectionTranslation,
                                    Story, StoryTranslation)

logger = logging.getLogger('storybase')

class GeoHashMultiValueField(indexes.MultiValueField):
    field_type = 'geohash'

class TextSpellField(indexes.CharField):
    field_type = 'textSpell'

class StoryIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.FacetCharField(model_attr='author')
    published = indexes.FacetDateTimeField(model_attr='published')
    created = indexes.FacetDateTimeField(model_attr='created')
    last_edited = indexes.FacetDateTimeField(model_attr='last_edited')
    # TODO: Use a meta class to dynamically populate these from "official"
    # tag sets 
    topic_ids = indexes.FacetMultiValueField()
    organization_ids = indexes.FacetMultiValueField()
    project_ids = indexes.FacetMultiValueField()
    language_ids = indexes.FacetMultiValueField()
    place_ids = indexes.FacetMultiValueField()
    points = GeoHashMultiValueField()
    num_points = indexes.IntegerField()
    suggestions = TextSpellField()

    def get_model(self):
        return Story

    def prepare_topic_ids(self, obj):
        return [topic.id for topic in obj.topics.all()]

    def prepare_organization_ids(self, obj):
        return [organization.organization_id for organization in obj.organizations.all()]

    def prepare_project_ids(self, obj):
        return [project.project_id for project in obj.projects.all()]

    def prepare_language_ids(self, obj):
        return obj.get_languages()

    def prepare_place_ids(self, obj):
        return [place.place_id for place in obj.inherited_places]

    def prepare_points(self, obj):
        return ["%s,%s" % (point[0], point[1]) for point in obj.points]

    def prepare_num_points(self, obj):
        return len(obj.points)

    def prepare(self, obj):
        prepared_data = super(StoryIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def index_queryset(self):
        """
        Get the default QuerySet to index when doing a full update.

        Excludes unpublish stories, template stories, and connected stories.
        """
        return Story.objects.filter(status__exact='published',
                                    is_template=False)\
                            .exclude(source__relation_type='connected')

    def should_update(self, instance, **kwargs):
        """
        Determine if an object should be updated in the index.
        """
        should_update = True
        translation_set = getattr(instance, instance.translation_set)
        if translation_set.count() == 0:
            should_update = False
        if 'action' in kwargs:
            # The signal is m2m_changed.  We only want to update
            # on the post actions
            if kwargs['action'] in ('pre_add', 'pre_remove', 'pre_clear'):
                should_update = False
        return should_update

    def should_remove_on_update(self, instance, **kwargs):
        if instance.status != 'published':
            return True

        if instance.is_template == True:
            return True

        if instance.is_connected() == True:
            return True

        return False

    def update_object(self, instance, using=None, **kwargs):
        """
        Update the index for a single object. Attached to the class's
        post-save hook.

        This version removes unpublished stories from the index
        """
        if self.should_remove_on_update(instance, **kwargs):
            self.remove_object(instance, using, **kwargs)
        else:
            super(StoryIndex, self).update_object(instance, using, **kwargs)

    def translation_update_object(self, sender, instance, **kwargs):
        """Signal handler for updating story index when the translation changes"""
        # Deal with race condition when stories are deleted
        # See issue #138
        try:
            self.update_object(instance.story)
        except Story.DoesNotExist:
            pass

    def location_update_object(self, sender, instance, **kwargs):
        """Signal handler for updating story index when a related location changes"""
        for story in instance.stories.all():
            self.update_object(story)

    def section_translation_update_object(self, sender, instance, **kwargs):
        """
        Signal handler for updating story index when a related section
        translation changes

        This is needed because the section titles in all languages are part
        of the document field of the index.

        """
        self.update_object(instance.section.story)

    def asset_translation_update_object(self, sender, instance, **kwargs):
        """
        Signal handler for updating story index when a related text asset
        translation changes

        This is needed because the text from text assets is part of the
        document field in the index.

        """
        stories = []
        if instance.asset.type == 'text':
            for section in instance.asset.sections.all():
                # Should I use a set here to make this faster?
                if section.story not in stories:
                    stories.append(section.story)

            for story in stories:
                self.update_object(story)

    def asset_relation_update_object(self, sender, instance, **kwargs):
        """
        Signal handler for when an asset to section relationship is 
        created or destroyed.

        This is needed because the text from assets is part of the 
        document field of the index.

        """
        if instance.asset.type == 'text':
            self.update_object(instance.section.story)
    
    def _setup_save(self):
        super(StoryIndex, self)._setup_save()
        # Update object when many-to-many fields change
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().organizations.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().projects.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().tags.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().topics.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().locations.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().places.through)

        signals.post_save.connect(self.asset_translation_update_object,
                                  sender=HtmlAssetTranslation)
        signals.post_save.connect(self.asset_relation_update_object,
                                  sender=SectionAsset)
        signals.post_delete.connect(self.asset_relation_update_object,
                                    sender=SectionAsset)
        signals.post_save.connect(self.section_translation_update_object,
                                  sender=SectionTranslation)
        signals.post_save.connect(self.translation_update_object,
                                  sender=StoryTranslation)
        signals.post_save.connect(self.location_update_object,
                                  sender=Location)

    def _teardown_save(self):
        super(StoryIndex, self)._teardown_save()
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().organizations.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().projects.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().topics.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().tags.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().locations.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().places.through)

        signals.post_save.disconnect(self.asset_translation_update_object,
                                     sender=HtmlAssetTranslation)
        signals.post_delete.disconnect(self.asset_relation_update_object,
                                       sender=SectionAsset)
        signals.post_save.disconnect(self.asset_relation_update_object,
                                     sender=SectionAsset)
        signals.post_save.disconnect(self.section_translation_update_object,
                                     sender=SectionTranslation)
        signals.post_save.disconnect(self.translation_update_object,
                                     sender=StoryTranslation)
        signals.post_save.disconnect(self.location_update_object,
                                     sender=Location)

    def _setup_delete(self):
        super(StoryIndex, self)._setup_delete()
        signals.post_delete.connect(self.translation_update_object,
                                    sender=StoryTranslation)

    def _teardown_delete(self):
        super(StoryIndex, self)._teardown_delete()
        signals.post_delete.disconnect(self.translation_update_object,
                                      sender=StoryTranslation)
