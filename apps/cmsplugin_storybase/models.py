from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.translation import get_language, ugettext_lazy as _
from cms.models.pluginmodel import CMSPlugin
from cms.models import Page
from cms.utils import i18n
from filer.fields.image import FilerImageField
from filer.models import Image 
from storybase.managers import FeaturedManager
from storybase.utils import unique_slugify
from storybase.fields import ShortTextField
from storybase.models import (PermissionMixin, PublishedModel,
        TimestampedModel, TranslatedModel, TranslationModel, 
        set_date_on_published)
from storybase_user.utils import format_user_name
from cmsplugin_storybase.managers import TeaserManager

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

    def get_absolute_url(self):
        kwargs = {'slug': self.slug}
        if self.published:
            kwargs['year'] = self.published.year
            kwargs['month'] = self.published.month
        else:
            kwargs['year'] = self.last_updated.year
            kwargs['month'] = self.last_updated.month

        # IMPORTANT: The AppHook needs to be connected in all languages
        # for the call to reverse() below to work correctly.
        # See http://docs.django-cms.org/en/2.1.3/extending_cms/app_integration.html#app-hooks
        # and http://stackoverflow.com/questions/11216565/django-cms-urls-used-by-apphooks-dont-work-with-reverse-or-url
        try:
            return reverse('newsitem_detail', kwargs=kwargs)
        except NoReverseMatch:
            return None 

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
    """
    Brief summary of a Page

    This is intended to be used when listing child pages on a top-level
    page.
    
    """
    teaser = models.TextField(blank=True)
    language = models.CharField(_("language"), max_length=15, db_index=True)
    page = models.ForeignKey(Page, verbose_name=_("page"), related_name="teaser_set")

    objects = TeaserManager()

    class Meta:
        unique_together = (('language', 'page'),)

    def __unicode__(self):
        return self.teaser


class EmptyTeaser(object):
    """
    Mock Teaser object 
    
    Lets us avoid branching in the admin code 
    """
    # This pattern was taken from Django CMS' Title implementation
    teaser = u''


def get_teaser(self, language=None, fallback=True, version_id=None, force_reload=False):
    """
    Get the teaser of the page depending on the given language
    """
    # This is based largely off of ``cms.models.Page.get_title``
    # but it doesn't bother with revisions and flattens out
    # the logic in ``get_title_obj_attribute``,
    # ``get_title_obj`` and ``_get_title_cache`` into a single
    # method
    if not language:
        language = get_language()
    load = False
    if not hasattr(self, 'teaser_cache') or force_reload:
        # No teasers have been cached. We need to load the
        # teaser from the database
        load = True
        # But first, create the cache attribute
        self.teaser_cache = {}
    elif not language in self.teaser_cache:
        # We have the cache set up, but the desired language
        # isn't cached.
        if fallback:
            # Check if we've cached the teaser in a fallback
            # language
            fallback_langs = i18n.get_fallback_languages(language)
            for lang in fallback_langs:
                if lang in self.teaser_cache:
                    # We found a teaser for the fallback
                    # language.  Return it!
                    return self.teaser_cache[lang].teaser
            # We didn't find teasers in any fallback language,
            # We'll try to load it from the database below
            load = True

    if load:
        # Use ``TeaserManager.get_teaser`` to handle
        # getting the ``Teaser`` instance from the database
        # wth language fallback
        teaser = Teaser.objects.get_teaser(self, language, language_fallback=fallback)
        if teaser:
            # We found a teaser. Cache it and then return it
            self.teaser_cache[teaser.language] = teaser
            return teaser.teaser

    # If all else fails, return an empty string
    return ""

# Patch the Page Model class to add our getter 
setattr(Page, 'get_teaser', get_teaser)


class StoryPlugin(CMSPlugin):
    story = models.ForeignKey('storybase_story.Story', related_name='plugins')

    def __unicode__(self):
        return self.story.title
