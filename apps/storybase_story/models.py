from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from taggit.managers import TaggableManager

from storybase_asset.models import Asset
from storybase_tag.models import OfficialTaggedItem

STORY_STATUS = (
    (u'draft', u'draft'),
    (u'published', u'published'),
)

class Story(models.Model):
    assets = models.ManyToManyField(Asset, related_name='stories')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STORY_STATUS, default='draft')
    teaser = models.TextField(blank=True)
    slug = models.SlugField()
    tags = TaggableManager(through=OfficialTaggedItem)
    author = models.ForeignKey(User, related_name="stories")

    class Meta:
        verbose_name_plural = "stories"

    def __unicode__(self):
        return self.title

class StoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "assets":
            kwargs["queryset"] = Asset.objects.filter(user=request.user)
        return super(StoryAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    
admin.site.register(Story, StoryAdmin)
