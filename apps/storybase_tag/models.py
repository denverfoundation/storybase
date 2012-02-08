from django.contrib import admin
from django.db import models

from taggit.models import TagBase, GenericTaggedItemBase

class OfficialTag(TagBase):
    official = models.BooleanField(default=False)

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"

class OfficialTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey('OfficialTag', related_name="%(app_label)s_%(class)s_items")


admin.site.register(OfficialTag)
