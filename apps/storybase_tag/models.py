from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.models import TagBase, GenericTaggedItemBase

class Tag(TagBase):
    official = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

admin.site.register(Tag)

class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey('Tag',  
                            related_name="%(app_label)s_%(class)s_items")

class TagSet(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    tags = models.ManyToManyField('Tag', related_name='tag_set',
                                  verbose_name=_('Tags'), blank=True)

    def __unicode__(self):
        return self.name

admin.site.register(TagSet)
