from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from django_dag.models import edge_factory, node_factory

# TODO: Decide on tagging suggestion admin app.
# Right now, I'm using a hacked version of
# https://bitbucket.org/fabian/django-taggit-autosuggest
# which I modified to allow for specifying a Tag model
# other than taggit.models.Tag
#from taggit_autosuggest.managers import TaggableManager

from uuidfield.fields import UUIDField

from storybase_asset.models import Asset
#from storybase_tag.models import TaggedItem

STORY_STATUS = (
    (u'draft', u'draft'),
    (u'published', u'published'),
)

class Story(models.Model):
    story_id = UUIDField(auto=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STORY_STATUS, default='draft')
    summary = models.TextField(blank=True)
    slug = models.SlugField()
    #tags = TaggableManager(through=TaggedItem, blank=True)
    author = models.ForeignKey(User, related_name="stories")
    pub_date = models.DateField(blank=True, null=True)
    last_edited = models.DateTimeField(default=datetime.now())
    assets = models.ManyToManyField(Asset, related_name='stories', blank=True)

    class Meta:
        verbose_name_plural = "stories"

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('story_detail', [str(self.slug)])

class Section(node_factory('SectionRelation')):
    """ Section of a story """
    section_id = UUIDField(auto=True)
    title = models.TextField()
    story = models.ForeignKey('Story', related_name='sections')
    # True if this section the root section of the story, either
    # the first section in a linear story, or the central node
    # in a drill-down/"spider" structure.  Otherwise, False
    root = models.BooleanField(default=False)
    assets = models.ManyToManyField(Asset, related_name='sections', blank=True, through='SectionAsset')

    def __unicode__(self):
        return self.title

    def inline_assets(self):
        return [asset.subclass() for asset in self.assets.exclude(type='article').order_by('sectionasset__weight')]

    def articles(self):
        return [asset.subclass() for asset in self.assets.filter(type='article').order_by('sectionasset__weight')] 

class SectionRelation(edge_factory(Section, concrete=False)):
    """ "Through" class for parent/child relationships between sections """
    weight = models.IntegerField(default=0)

class SectionAsset(models.Model):
    """ "Through" class for Asset to Section relations """
    section = models.ForeignKey('Section')
    asset = models.ForeignKey('storybase_asset.Asset')
    weight = models.IntegerField(default=0)
