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

        # XXX: ZM Additional Hack http://stackoverflow.com/questions/17520812/how-to-resolve-circular-import-involving-haystack

        MyHtmlAssetTranslation = get_model('storybase_asset', 'HtmlAssetTranslation')
        MyLocation = get_model('storybase_geo', 'Location')
        MySectionAsset = get_model('storybase_story', 'SectionAsset')
        MySectionTranslation = get_model('storybase_story', 'SectionTranslation')
        MyStory = get_model('storybase_story', 'Story')
        MyStoryTranslation = get_model('storybase_story', 'StoryTranslation')

        # Save signals
        signals.post_save.connect(self.handle_save, sender=MyStory)
        signals.post_save.connect(self.handle_translation_save,
                                  sender=MyStoryTranslation)

        # Update object when many-to-many fields change
        signals.m2m_changed.connect(self.handle_save, sender=MyStory.organizations.through)
        signals.m2m_changed.connect(self.handle_save, sender=MyStory.projects.through)
        signals.m2m_changed.connect(self.handle_save, sender=MyStory.tags.through)
        signals.m2m_changed.connect(self.handle_save, sender=MyStory.topics.through)
        signals.m2m_changed.connect(self.handle_save, sender=MyStory.locations.through)
        signals.m2m_changed.connect(self.handle_save, sender=MyStory.places.through)

        signals.post_save.connect(self.handle_asset_translation_save,
                                  sender=MyHtmlAssetTranslation)
        signals.post_save.connect(self.handle_asset_relation_save,
                                  sender=MySectionAsset)
        signals.post_delete.connect(self.handle_asset_relation_save,
                                    sender=MySectionAsset)
        signals.pre_delete.connect(self.handle_cache_story_for_delete,
                                   sender=MySectionAsset)
        signals.post_save.connect(self.handle_section_translation_save,
                                  sender=MySectionTranslation)
        signals.post_save.connect(self.handle_location_save,
                                  sender=MyLocation)

        # Delete signals
        signals.post_delete.connect(self.handle_delete, sender=MyStory)
        signals.post_delete.connect(self.handle_translation_save,
                                    sender=MyStoryTranslation)

    def _setup_help(self):
        # HACK: Import here to avoid circular import
        # See http://stackoverflow.com/a/17364366/386210

        # XXX: ZM Additional Hack http://stackoverflow.com/questions/17520812/how-to-resolve-circular-import-involving-haystack

        MyHelp = get_model('storybase_help', 'Help')
        MyHelpTranslation = get_model('storybase_help', 'HelpTranslation')

        signals.post_save.connect(self.handle_save, sender=MyHelp)
        signals.post_save.connect(self.handle_translation_save,
                                  sender=MyHelpTranslation)
        signals.post_delete.connect(self.handle_delete, sender=MyHelp)
        signals.post_delete.connect(self.handle_translation_save,
                                    sender=MyHelpTranslation)

    def _teardown_story(self):
        # HACK: Import here to avoid circular import
        # See http://stackoverflow.com/a/17364366/386210

        # XXX: ZM Additional Hack http://stackoverflow.com/questions/17520812/how-to-resolve-circular-import-involving-haystack

        MyHtmlAssetTranslation = get_model('storybase_story', 'HtmlAssetTranslation')
        MyLocation = get_model('storybase_story', 'Location')
        MySectionAsset = get_model('storybase_story', 'SectionAsset')
        MySectionTranslation = get_model('storybase_story', 'SectionTranslation')
        MyStory = get_model('storybase_story', 'Story')
        MyStoryTranslation = get_model('storybase_story', 'StoryTranslation')

        signals.post_save.disconnect(self.handle_save, sender=MyStory)
        signals.post_save.disconnect(self.handle_translation_save,
                                     sender=MyStoryTranslation)

        signals.m2m_changed.disconnect(self.handle_save, sender=MyStory.organizations.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=MyStory.projects.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=MyStory.tags.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=MyStory.topics.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=MyStory.locations.through)
        signals.m2m_changed.disconnect(self.handle_save, sender=MyStory.places.through)


        signals.post_save.disconnect(self.handle_asset_translation_save,
                                  sender=MyHtmlAssetTranslation)
        signals.post_save.disconnect(self.handle_asset_relation_save,
                                     sender=MySectionAsset)
        signals.post_delete.disconnect(self.handle_asset_relation_save,
                                       sender=MySectionAsset)
        signals.post_save.disconnect(self.handle_section_translation_save,
                                     sender=MySectionTranslation)
        signals.post_save.disconnect(self.handle_location_save,
                                     sender=MyLocation)

        signals.post_delete.disconnect(self.handle_delete, sender=MyStory)
        signals.post_delete.disconnect(self.handle_translation_save,
                                       sender=MyStoryTranslation)

    def _teardown_help(self):
        # HACK: Import here to avoid circular import

        # XXX: ZM Additional Hack http://stackoverflow.com/questions/17520812/how-to-resolve-circular-import-involving-haystack

        MyHelp = get_model('storybase_help', 'Help')
        MyHelpTranslation = get_model('storybase_help', 'HelpTranslation')

        signals.post_save.disconnect(self.handle_save, sender=MyHelp)
        signals.post_save.disconnect(self.handle_translation_save,
                                     sender=MyHelpTranslation)
        signals.post_delete.disconnect(self.handle_delete, sender=MyHelp)
        signals.post_delete.disconnect(self.handle_translation_save,
                                       sender=MyHelpTranslation)

    def setup(self):
        self._setup_story()
        self._setup_help()

    def teardown(self):
        self._teardown_story()
        self._teardown_help()
