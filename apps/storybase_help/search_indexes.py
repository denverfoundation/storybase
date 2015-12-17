from haystack import indexes

from storybase.search.fields import TextSpellField
from storybase_help.models import Help

class HelpIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    suggestions = TextSpellField()

    def get_model(self):
        return Help

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(searchable=True)

    def prepare(self, obj):
        prepared_data = super(HelpIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def should_remove_on_update(self, instance, **kwargs):
        if not instance.searchable:
            return True

        return False

    def update_object(self, instance, using=None, **kwargs):
        """
        Update the index for a single object. Attached to the class's
        post-save hook.

        This version removes help items no longer tagged as searchable from
        the index

        """
        if self.should_remove_on_update(instance, **kwargs):
            self.remove_object(instance, using, **kwargs)
        else:
            super(HelpIndex, self).update_object(instance, using, **kwargs)

    def translation_update_object(self, instance, **kwargs):
        """Signal handler for updating search index when the translation changes"""
        # Deal with race condition when items are deleted
        # See issue #138
        try:
            self.update_object(instance.help)
        except Help.DoesNotExist:
            pass
