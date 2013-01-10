from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from filer.fields.image import FilerImageField
from cms.models.pluginmodel import CMSPlugin
from storybase.utils import unique_slugify
from storybase.fields import ShortTextField
from storybase.models import (PublishedModel, TimestampedModel, 
        TranslatedModel, TranslationModel, set_date_on_published)
       

class List(CMSPlugin):
    num_items = models.IntegerField(default=3)


class NewsItemTranslation(TranslationModel):
    news_item = models.ForeignKey('NewsItem')
    title = ShortTextField(blank=True) 
    body = models.TextField(blank=True)
    image = FilerImageField(null=True)

    class Meta:
        """Model metadata options"""
        unique_together = (('news_item', 'language'))

    def __unicode__(self):
        return self.title


class NewsItem(PublishedModel, TimestampedModel, TranslatedModel):
    author = models.ForeignKey(User, related_name="news_items", blank=True,
                               null=True)
    slug = models.SlugField(blank=True)

    translated_fields = ['title', 'body', 'image',] 
    translation_set = 'newsitemtranslation_set'
    translation_class = NewsItemTranslation


def set_slug(sender, instance, **kwargs):
    try:
        if not instance.news_item.slug:
            unique_slugify(instance.news_item, instance.title)
        instance.news_item.save()
    except NewsItem.DoesNotExist:
        # Instance doesn't have a related News Item.
        # Encountered this when loading fixture
        pass


pre_save.connect(set_date_on_published, sender=NewsItem)
post_save.connect(set_slug, sender=NewsItemTranslation)


class StoryPlugin(CMSPlugin):
    story = models.ForeignKey('storybase_story.Story', related_name='plugins')

    def __unicode__(self):
        return self.story.title
