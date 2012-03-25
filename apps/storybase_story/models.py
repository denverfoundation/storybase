from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.utils.safestring import mark_safe
from django_dag.models import edge_factory, node_factory
# TODO: Decide on tagging suggestion admin app.
# Right now, I'm using a hacked version of
# https://bitbucket.org/fabian/django-taggit-autosuggest
# which I modified to allow for specifying a Tag model
# other than taggit.models.Tag
#from taggit_autosuggest.managers import TaggableManager
from uuidfield.fields import UUIDField
from storybase.fields import ShortTextField
from storybase.models import (LicensedModel, PublishedModel,
    TimestampedModel, TranslatedModel, TranslationModel,
    DEFAULT_LICENSE, DEFAULT_STATUS,
    set_date_on_published)
from storybase.utils import slugify
from storybase_asset.models import Asset
from storybase_user.models import Organization, Project
#from storybase_tag.models import TaggedItem

class StoryTranslation(TranslationModel):
    story = models.ForeignKey('Story')
    title = ShortTextField() 
    summary = models.TextField(blank=True)
    slug = models.SlugField()

    class Meta:
        unique_together = (('story', 'language'))

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ Overriding save to automatically set slug """
        if not self.slug:
            self.slug = slugify(self.title)
        super(StoryTranslation, self).save(*args, **kwargs)

class Story(TranslatedModel, LicensedModel, PublishedModel, 
            TimestampedModel):
    story_id = UUIDField(auto=True)
    byline = models.TextField()
    # blank=True, null=True to bypass validation so the user doesn't
    # have to always remember to set this in the Django admin.
    # Though this is set to blank=True, null=True, we should always set
    # this value.  In fact, the StoryModelAdmin class sets this to
    # request.user
    author = models.ForeignKey(User, related_name="stories", blank=True, null=True)
    assets = models.ManyToManyField(Asset, related_name='stories', blank=True)
    organizations = models.ManyToManyField(Organization, related_name='stories', blank=True)
    projects = models.ManyToManyField(Project, related_name='stories',
        blank=True)
    #tags = TaggableManager(through=TaggedItem, blank=True)

    translated_fields = ['title', 'summary', 'slug']
    translation_set = 'storytranslation_set'

    class Meta:
        verbose_name_plural = "stories"

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('story_detail', [str(self.story_id)])

    def get_root_section(self):
        """ Return the root section """
        return self.sections.get(root=True)

    def render_story_structure(self, format='html'):
        """ Render a representation of the Story structure based on its sections """
        try:
            root = self.get_root_section()
        except Section.DoesNotExist:
            return ''

        return root.render(format)

# Hook up some signal handlers
pre_save.connect(set_date_on_published, sender=Story)

class Section(node_factory('SectionRelation'), TranslatedModel):
    """ Section of a story """
    section_id = UUIDField(auto=True)
    story = models.ForeignKey('Story', related_name='sections')
    # True if this section the root section of the story, either
    # the first section in a linear story, or the central node
    # in a drill-down/"spider" structure.  Otherwise, False
    root = models.BooleanField(default=False)
    assets = models.ManyToManyField(Asset, related_name='sections', blank=True, through='SectionAsset')

    translated_fields = ['title']
    translation_set = 'sectiontranslation_set'

    def __unicode__(self):
        return self.title

    def render(self, format='html'):
        try:
            return getattr(self, "render_" + format).__call__()
        except AttributeError:
            return self.__unicode__()

    def render_html(self):
        output = []
        output.append("<h4>%s</h4>" % self.title)
        if self.assets.count() > 0:
            output.append("<h5>Assets</h5>")
            output.append("<ul>")
            for asset in self.assets.order_by('sectionasset__weight'):
                output.append("<li>%s</li>" % asset.title)
            output.append("</ul>")

        # TODO: Render connected assets

        return mark_safe(u'\n'.join(output))

class SectionTranslation(TranslationModel):
    section = models.ForeignKey('Section')
    title = ShortTextField() 

    class Meta:
        unique_together = (('section', 'language'))

    def __unicode__(self):
        return self.title

class SectionRelation(edge_factory(Section, concrete=False)):
    """ "Through" class for parent/child relationships between sections """
    weight = models.IntegerField(default=0)

class SectionAsset(models.Model):
    """ "Through" class for Asset to Section relations """
    section = models.ForeignKey('Section')
    asset = models.ForeignKey('storybase_asset.Asset')
    weight = models.IntegerField(default=0)

def create_story(title, summary='', byline='', author=None, status=DEFAULT_STATUS, license=DEFAULT_LICENSE, language=settings.LANGUAGE_CODE, *args, **kwargs):
    """ Convenience function for creating a Story

    Allows for the creation of stories without having to explicitly
    deal with the translations.

    """
    obj = Story(
        byline=byline,
        author=author,
        status=status)
    obj.save()
    translation = StoryTranslation(story=obj, title=title, summary=summary, language=language)
    translation.save()
    return obj
