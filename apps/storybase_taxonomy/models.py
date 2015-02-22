from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager

from categories.base import CategoryManager
from categories.settings import SLUG_TRANSLITERATOR

from taggit.models import TagBase, GenericTaggedItemBase

from uuidfield.fields import UUIDField

from storybase.models import TranslatedModel, TranslationModel, PermissionMixin
from storybase.utils import slugify

class CategoryTranslationBase(TranslationModel):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'))

    class Meta:
        abstract = True

    def __unicode__(self):
        return force_unicode(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(SLUG_TRANSLITERATOR(self.name))[:50]

        super(CategoryTranslationBase, self).save(*args, **kwargs)


class TranslatedCategoryBase(MPTTModel, TranslatedModel):
    """
    A version of CategoryBase from the categories app that supports a
    translated name and slug field.
    """
    parent = TreeForeignKey('self',
        blank=True,
        null=True,
        related_name="children",
        verbose_name='Parent')
    active = models.BooleanField(default=True)

    objects = CategoryManager()
    tree = TreeManager()


    def save(self, *args, **kwargs):
        """
        While you can activate an item without activating its descendants,
        It doesn't make sense that you can deactivate an item and have its
        decendants remain active.
        """
        super(TranslatedCategoryBase, self).save(*args, **kwargs)

        if not self.active:
            for item in self.get_descendants():
                if item.active != self.active:
                    item.active = self.active
                    item.save()

    def __unicode__(self):
        ancestors = self.get_ancestors()
        return ' > '.join([force_unicode(i.name) for i in ancestors]+[self.name,])

    class Meta:
        abstract = True
        ordering = ('tree_id', 'lft')

    # TODO: Figure out if we need to order categories by some field.
    # We could add a weight field to the model, or save a copy of the first
    # translation's name field.
    #class MPTTMeta:
    #    order_insertion_by = 'weight'


class CategoryTranslation(CategoryTranslationBase):
    category = models.ForeignKey('Category')

    class Meta:
        unique_together = (('category', 'language'))


class Category(TranslatedCategoryBase):
    translation_set = 'categorytranslation_set'
    translated_fields = ['name', 'slug']

    def get_absolute_url(self):
        return reverse('topic_stories', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "categories"


class TagPermission(PermissionMixin):
    def user_can_change(self, user):
        return False

    def user_can_add(self, user):
        if user.is_active:
            return True

        return False

    def user_can_delete(self, user):
        return self.user_can_change(user)


class Tag(TagPermission, TagBase):
    tag_id = UUIDField(auto=True)

    def get_absolute_url(self):
        return reverse('tag_stories', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(Tag, related_name='items')


def create_category(name, slug='', language=settings.LANGUAGE_CODE,
                 *args, **kwargs):
    """Convenience function for creating a Category

    Allows for the creation of categories without having to explicitly
    deal with the translations.

    """
    obj = Category(*args, **kwargs)
    obj.save()
    translation = CategoryTranslation(category=obj, name=name, slug=slug,
                                      language=language)
    translation.save()
    return obj


def create_categories(names):
    """Convenience function for creating a categories

    Allows for the creation of categories without having to deal
    with slugs, or translations. The categories will only be created
    if they do not exist.

    Returns a list of newly created categories.

    """

    categories = []

    for name in names:
        if not CategoryTranslation.objects.filter(name=name).exists():
            c = create_category(
                name=name,
                slug=slugify(name)
            )

            categories.append(c)

    return categories
