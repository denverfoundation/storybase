from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.models import TagBase, GenericTaggedItemBase

class Tag(TagBase):
    official = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Tag, TagAdmin)

class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey('Tag',  
                            related_name="%(app_label)s_%(class)s_items")

class TagSet(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    official = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', related_name='tag_set',
                                  verbose_name=_('Tags'), blank=True)

    def __unicode__(self):
        return self.name

class TagSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'official')

admin.site.register(TagSet, TagSetAdmin)
