from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext_lazy as _

from cms.extensions import TitleExtension
from cms.extensions.extension_pool import extension_pool
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


class ActivityTranslation(TranslationModel):
    activity = models.ForeignKey('Activity')
    title = ShortTextField()
    description = models.TextField()
    supplies = models.TextField(blank=True, verbose_name=_("Required supplies"))
    time = models.CharField(max_length=200, blank=True,
        verbose_name=_("Time it takes to do"))
    num_participants = models.CharField(max_length=200, blank=True,
        verbose_name=_("Number of participants"))
    # This is a text field, rather than something more structured,
    # because there are a variable number of handouts, and each handout
    # can have a variable number of formats (PDF, Google Doc, Floodlight
    # Story, etc.)
    links = models.TextField(blank=True,
        verbose_name=_("Links to the full activity"),
        help_text=_("These are materials/handouts we have been using in "
            "Story-Rasings"))


class Activity(TranslatedModel):
    """
    Metadata for a storytelling activity
    
    This content is similar to Mozilla's Webmaker guides:

    * Overview - https://webmaker.org/event-guides
    * Example guide (Hack Jam) - https://webmaker.makes.org/thimble/host-a-hackjam
    * Hactivities menu - http://hivenyc.org/hacktivityGrid.html

    """
    slug = models.SlugField(blank=True,
        help_text=_("A short, unique label for this activity. It is also "
                    "used to build URLs for the activity. This field can only "
                    "contain letters, numbers, underscores or hyphens"))
    # This will be used as the thumbnail when activities are aggregated
    image = FilerImageField(blank=True, null=True,
        help_text=_("Image used as the thumbnail when activities are listed. "
                    "Additional images can be shown on the related CMS page"))
    page = models.OneToOneField(Page, blank=True, null=True,
        help_text=_("CMS page that provides additional, free-form information "
                    "about thei activity"))

    translated_fields = ['title', 'description', 'supplies', 'time',
                         'num_participants', 'links']
    translation_set = 'activitytranslation_set'
    translation_class = ActivityTranslation

    class Meta:
        verbose_name_plural = _("Activities")

    def __unicode__(self):
        return self.title

def set_activity_slug(sender, instance, **kwargs):
    try:
        if not instance.activity.slug:
            unique_slugify(instance.activity, instance.title)
        instance.activity.save()
    except Activity.DoesNotExist:
        # Instance doesn't have a related Activity.
        # Encountered this when loading fixture
        pass

post_save.connect(set_activity_slug, sender=ActivityTranslation)


class ActivityPlugin(CMSPlugin):
    activity = models.ForeignKey(Activity, related_name='plugins')

    def __unicode__(self):
        return self.activity.title


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

    def get_absolute_url(self):
        kwargs = {'slug': self.slug}
        if self.published:
            kwargs['year'] = self.published.year
            kwargs['month'] = self.published.month
        else:
            kwargs['year'] = self.last_edited.year
            kwargs['month'] = self.last_edited.month

        # IMPORTANT: The AppHook needs to be connected in all languages
        # for the call to reverse() below to work correctly.
        # See http://docs.django-cms.org/en/2.1.3/extending_cms/app_integration.html#app-hooks
        # and http://stackoverflow.com/questions/11216565/django-cms-urls-used-by-apphooks-dont-work-with-reverse-or-url
        try:
            return reverse('newsitem_detail', kwargs=kwargs)
        except NoReverseMatch:
            return ""

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
            "url": self.get_absolute_url(),
        }


def set_newsitem_slug(sender, instance, **kwargs):
    try:
        if not instance.news_item.slug:
            unique_slugify(instance.news_item, instance.title)
        instance.news_item.save()
    except NewsItem.DoesNotExist:
        # Instance doesn't have a related News Item.
        # Encountered this when loading fixture
        pass


pre_save.connect(set_date_on_published, sender=NewsItem)
post_save.connect(set_newsitem_slug, sender=NewsItemTranslation)


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


class TeaserExtension(TitleExtension):
    teaser = models.TextField(blank=True,
        help_text=_("Brief description of the page to be "
                    "included on parent pages"))

    def __unicode__(self):
        return self.teaser

extension_pool.register(TeaserExtension)


class StoryPlugin(CMSPlugin):
    story = models.ForeignKey('storybase_story.Story', related_name='plugins')

    def __unicode__(self):
        return self.story.title


class HelpPlugin(CMSPlugin):
    help = models.ForeignKey('storybase_help.Help', related_name='plugins')

    def __unicode__(self):
        return self.help.title
