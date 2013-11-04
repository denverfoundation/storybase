from django.db.models import signals
from django.db.models.loading import get_model

from haystack.exceptions import NotHandled
from haystack.signals import RealtimeSignalProcessor as HaystackRealtimeSignalProcessor


class RealtimeSignalProcessor(HaystackRealtimeSignalProcessor):
    """
    Custom Haystack signal processor
    
    This signal processor only connects to signals for the Story
    and Help (and related) models instead of connecting to the
    ``post_save`` and ``post_delete`` signals of all models

    It also connects signal handlers to signals on translations
    and other related models.
    """

    # Translate sender model classes to the model classes that
    # actually have an index
    #
    # The class names mapp to a list appropriate for the input
    # to ``django.db.models.loading.get_model()`` to avoid
    # importing the model directly and causing a circular
    # import. See http://stackoverflow.com/a/17364366/386210
    _SENDER_MAP = {
        'HtmlAssetTranslation': ['storybase_story', 'Story'],
        'Location': ['storybase_story', 'Story'],
        'HelpTranslation': ['storybase_help', 'Help'],
        'SectionAsset': ['storybase_story', 'Story'],
        'SectionTranslation': ['storybase_story', 'Story'],
        'StoryTranslation': ['storybase_story', 'Story'],
    }

    def _get_index(self, using, sender):
        """
        Get the search index for a model

        This is needed because we update some indexes based on
        changes on related models
        """
        if sender.__name__ in self._SENDER_MAP:
            index_class = get_model(*self._SENDER_MAP[sender.__name__])
        else:
            index_class = sender 

        return self.connections[using].get_unified_index().get_index(index_class)

    def handle_method(self, method_name, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        update should be sent to & update the backend
        using the ``SearchIndex`` method specified in ``method_name``.
        """
        using_backends = self.connection_router.for_write(instance=instance)

        for using in using_backends:
            try:
                index = self._get_index(using, sender)
                index_method = getattr(index, method_name)
                index_method(instance, using=using)
            except NotHandled:
                # TODO: Maybe log it or let the exception bubble?
                pass

    def handle_save(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        update should be sent to & update the object on those backends.
        """
        self.handle_method('update_object', sender, instance, **kwargs)

    def handle_delete(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        delete should be sent to & delete the object on those backends.
        """
        self.handle_method('remove_object', sender, instance, **kwargs)

    def handle_asset_translation_save(self, sender, instance, **kwargs):
        self.handle_method('asset_translation_update_object', sender, instance, **kwargs)

    def handle_asset_relation_save(self, sender, instance, **kwargs):
        self.handle_method('asset_relation_update_object', sender, instance, **kwargs)

    def handle_cache_story_for_delete(self, sender, instance, **kwargs):
        self.handle_method('cache_story_for_delete', sender, instance, **kwargs)

    def handle_section_translation_save(self, sender, instance, **kwargs):
        self.handle_method('section_translation_update_object', sender, instance, **kwargs)

    def handle_translation_save(self, sender, instance, **kwargs):
        self.handle_method('translation_update_object', sender, instance, **kwargs)

    def handle_location_save(self, sender, instance, **kwargs):
        self.handle_method('location_update_object', sender, instance, **kwargs)

    def _setup_story(self):
        # HACK: Import here to avoid circular import
        # See http://stackoverflow.com/a/17364366/386210
        from storybase_asset.models import HtmlAssetTranslation
        from storybase_geo.models import Location
        from storybase_story.models import (SectionAsset, SectionTranslation,
                                    Story, StoryTranslation)

        # Save signals
        signals.post_save.connect(self.handle_save, sender=Story)
        signals.post_save.connect(self.handle_translation_save,
                                  sender=StoryTranslation)

        # Update object when many-to-many fields change
        signals.m2m_changed.connect(self.handle_save, sender=Story.organizations.through)
        signals.m2m_changed.connect(self.handle_save, sender=Story.projects.through)
        signals.m2m_changed.connect(self.handle_save, sender=Story.tags.through)
        signals.m2m_changed.connect(self.handle_save, sender=Story.topics.through)
        signals.m2m_changed.connect(self.handle_save, sender=Story.locations.through)
        signals.m2m_changed.connect(self.handle_save, sender=Story.places.through)

        signals.post_save.connect(self.handle_asset_translation_save,
                                  sender=HtmlAssetTranslation)
        signals.post_save.connect(self.handle_asset_relation_save,
                                  sender=SectionAsset)
        signals.post_delete.connect(self.handle_asset_relation_save,
                                    sender=SectionAsset)
        signals.pre_delete.connect(self.handle_cache_story_for_delete,
                                   sender=SectionAsset)
        signals.post_save.connect(self.handle_section_translation_save,
                                  sender=SectionTranslation)
        signals.post_save.connect(self.handle_location_save,
                                  sender=Location)

        # Delete signals
        signals.post_delete.connect(self.handle_delete, sender=Story)
        signals.post_delete.connect(self.handle_translation_save,
                                    sender=StoryTranslation)

    def _setup_help(self):
        # HACK: Import here to avoid circular import
        # See http://stackoverflow.com/a/17364366/386210
        from storybase_help.models import Help, HelpTranslation

        signals.post_save.connect(self.handle_save, sender=Help)
        signals.post_save.connect(self.handle_translation_save,
                                  sender=HelpTranslation)
        signals.post_delete.connect(self.handle_delete, sender=Help)
        signals.post_delete.connect(self.handle_translation_save,
                                    sender=HelpTranslation)

    def _teardown_story(self):
        # HACK: Import here to avoid circular import
        # See http://stackoverflow.com/a/17364366/386210
        from storybase_asset.models import HtmlAssetTranslation
        from storybase_geo.models import Location
        from storybase_story.models import (SectionAsset, SectionTranslation,
                                    Story, StoryTranslation)

        signals.post_save.disconnect(self.handle_save, sender=Story)
        signals.post_save.disconnect(self.handle_translation_save,
                                     sender=StoryTranslation)

        signals.m2m_changed.disconnect(self.handle_save, sender=Story.organizations.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=Story.projects.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=Story.tags.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=Story.topics.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=Story.locations.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=Story.places.through)


        signals.post_save.disconnect(self.handle_asset_translation_save,
                                  sender=HtmlAssetTranslation)
        signals.post_save.disconnect(self.handle_asset_relation_save,
                                     sender=SectionAsset)
        signals.post_delete.disconnect(self.handle_asset_relation_save,
                                       sender=SectionAsset)
        signals.post_save.disconnect(self.handle_section_translation_save,
                                     sender=SectionTranslation)
        signals.post_save.disconnect(self.handle_location_save,
                                     sender=Location)

        signals.post_delete.disconnect(self.handle_delete, sender=Story)
        signals.post_delete.disconnect(self.handle_translation_save,
                                       sender=StoryTranslation)

    def _teardown_help(self):
        # HACK: Import here to avoid circular import
        # See http://stackoverflow.com/a/17364366/386210
        from storybase_help.models import Help, HelpTranslation

        signals.post_save.disconnect(self.handle_save, sender=Help)
        signals.post_save.disconnect(self.handle_translation_save,
                                     sender=HelpTranslation)
        signals.post_delete.disconnect(self.handle_delete, sender=Help)
        signals.post_delete.disconnect(self.handle_translation_save,
                                       sender=HelpTranslation)

    def setup(self):
        self._setup_story()
        self._setup_help()

    def teardown(self):
        self._teardown_story()
        self._teardown_help()
