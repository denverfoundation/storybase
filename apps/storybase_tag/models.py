from django.contrib import admin
from django.db import models

from taggit.models import TagBase, GenericTaggedItemBase

class OfficialTag(TagBase):
    official = models.BooleanField(default=False)

class OfficialTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey('OfficialTag')

admin.site.register(OfficialTag)
