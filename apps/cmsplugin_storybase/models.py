from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext_lazy as _
from cms.models.pluginmodel import CMSPlugin
from cms.models import Page
from filer.fields.image import FilerImageField
from filer.models import Image 
from storybase.managers import FeaturedManager
from storybase.utils import unique_slugify
from storybase.fields import ShortTextField
from storybase.models import (PermissionMixin, PublishedModel,
        TimestampedModel, TranslatedModel, TranslationModel, 
        set_date_on_published)
from storybase_user.utils import format_user_name

class List(CMSPlugin):
    num_items = models.IntegerField(default=3)


class NewsItemPermission(PermissionMixin):
    """Permissions for the NewsItem model"""
    def user_can_view(self, user):
        from storybase_user.utils import is_admin

        if self.status == 'published':
            return True

        if self.author == user:
            return True

        if user.is_superuser or is_admin(user):
            return True

        return False

    def anonymoususer_can_view(self, user):
        if self.status == 'published':
            return True

        return False


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


class NewsItem(NewsItemPermission, PublishedModel, TimestampedModel, 
        TranslatedModel):
    author = models.ForeignKey(User, related_name="news_items", blank=True,
                               null=True)
    slug = models.SlugField(blank=True)
    on_homepage = models.BooleanField(_("Featured on homepage"),
                                      default=False)

    objects = FeaturedManager()
        
    translated_fields = ['title', 'body', 'image',] 
    translation_set = 'newsitemtranslation_set'
    translation_class = NewsItemTranslation

    def normalize_for_view(self, img_width):
        """Return attributes as a dictionary for use in a view context
        
        This allows using the same template across different models with
        differently-named attributes that hold similar information.

        """
        return {
            "type": _("News"),
            "title": self.title,
            "author": format_user_name(self.author),
            "date": self.created, 
            "image_html":' <img src="%s" />' % (self.image.url),
            "excerpt": self.body,
        }


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


def create_news_item(title, body, image=None, image_filename=None,
        language=settings.LANGUAGE_CODE, **kwargs):
    """Convenience function for creating a NewsItem"""
    translation_kwargs = {
        'title': title,
        'body': body,
        'language': language
    }
    if image:
        image_file = File(image, name=image_filename)
        translation_kwargs['image'] = Image.objects.create(
                owner=kwargs.get('owner', None),
                original_filename=image_filename,
               file=image_file)
    obj = NewsItem(**kwargs)
    obj.save()
    translation_kwargs['news_item'] = obj
    translation = NewsItemTranslation(**translation_kwargs)
    translation.save()
    return obj


class Teaser(models.Model):
    teaser = models.TextField(blank=True)
    language = models.CharField(_("language"), max_length=15, db_index=True)
    page = models.ForeignKey(Page, verbose_name=_("page"), related_name="teaser_set")

    class Meta:
        unique_together = (('language', 'page'),)


class EmptyTeaser(object):
    teaser = u''


class StoryPlugin(CMSPlugin):
    story = models.ForeignKey('storybase_story.Story', related_name='plugins')

    def __unicode__(self):
        return self.story.title
