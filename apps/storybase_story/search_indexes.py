import logging

from django.db.models import signals

from haystack import indexes

from storybase_geo.models import Location
from storybase_story.models import Story, StoryTranslation

logger = logging.getLogger('storybase')

class GeoHashMultiValueField(indexes.MultiValueField):
    field_type = 'geohash'

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
        if 'action' in kwargs:
            # The signal is m2m_changed.  We only want to update
            # on the post actions
            if kwargs['action'] in ('pre_add', 'pre_remove', 'pre_clear'):
                should_update = False
        return should_update

    def should_remove_on_update(self, instance, **kwargs):
        if instance.status != 'published':
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

    def _setup_save(self):
        super(StoryIndex, self)._setup_save()
        # Update object when many-to-many fields change
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().organizations.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().projects.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().topics.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().locations.through)
        signals.m2m_changed.connect(self.update_object, sender=self.get_model().places.through)

        signals.post_save.connect(self.translation_update_object,
                                  sender=StoryTranslation)
        signals.post_save.connect(self.location_update_object,
                                  sender=Location)

    def _teardown_save(self):
        super(StoryIndex, self)._teardown_save()
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().organizations.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().projects.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().topics.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().locations.through)
        signals.m2m_changed.disconnect(self.update_object, sender=self.get_model().places.through)

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
