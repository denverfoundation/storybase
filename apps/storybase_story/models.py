from django.contrib.auth.models import User
from django.db import models

# TODO: Decide on tagging suggestion admin app.
# Right now, I'm using a hacked version of
# https://bitbucket.org/fabian/django-taggit-autosuggest
# which I modified to allow for specifying a Tag model
# other than taggit.models.Tag
from taggit_autosuggest.managers import TaggableManager

from storybase_asset.models import Asset
from storybase_tag.models import TaggedItem

STORY_STATUS = (
    (u'draft', u'draft'),
    (u'published', u'published'),
)

class StoryAsset(models.Model):
    story = models.ForeignKey('Story')
    asset = models.ForeignKey('storybase_asset.Asset')
    weight = models.IntegerField(default=0)

class Story(models.Model):
    assets = models.ManyToManyField(Asset, related_name='stories', blank=True, through='StoryAsset')
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STORY_STATUS, default='draft')
    teaser = models.TextField(blank=True)
    slug = models.SlugField()
    tags = TaggableManager(through=TaggedItem)
    author = models.ForeignKey(User, related_name="stories")
    pub_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "stories"

    def __unicode__(self):
        return self.title

