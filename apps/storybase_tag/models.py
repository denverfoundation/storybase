from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.models import TagBase, GenericTaggedItemBase

class Tag(TagBase):
    official = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey('Tag',  
                            related_name="%(app_label)s_%(class)s_items")


admin.site.register(Tag)
