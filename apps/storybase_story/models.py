"""Models for stories and story sections"""

from django.conf import settings
from django.contrib.auth.models import User
from django.core import urlresolvers
from django.db import models
from django.db.models.signals import post_save, pre_save
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
    set_date_on_published)
from storybase.utils import slugify
from storybase_asset.models import Asset
from storybase_user.models import Organization, Project
#from storybase_tag.models import TaggedItem

class StoryTranslation(TranslationModel):
    """Encapsulates translated fields of a Story"""
    story = models.ForeignKey('Story')
    title = ShortTextField() 
    summary = models.TextField(blank=True)
    slug = models.SlugField()

    class Meta:
        """Model metadata options"""
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
    """Metadata for a story

    The Story model stores a story's metadata and aggregates a story's
    media assets

    """
    story_id = UUIDField(auto=True)
    byline = models.TextField()
    # blank=True, null=True to bypass validation so the user doesn't
    # have to always remember to set this in the Django admin.
    # Though this is set to blank=True, null=True, we should always set
    # this value.  In fact, the StoryModelAdmin class sets this to
    # request.user
    author = models.ForeignKey(User, related_name="stories", blank=True,
                               null=True)
    assets = models.ManyToManyField(Asset, related_name='stories',
                                    blank=True)
    organizations = models.ManyToManyField(Organization,
                                           related_name='stories',
                                           blank=True)
    projects = models.ManyToManyField(Project, related_name='stories',
                                      blank=True)
    #tags = TaggableManager(through=TaggedItem, blank=True)

    translated_fields = ['title', 'summary', 'slug']
    translation_set = 'storytranslation_set'

    class Meta:
        """Model metadata options"""
        verbose_name_plural = "stories"

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        """Calculate the canonical URL for a Story"""
        return ('story_detail', [str(self.story_id)])

    def get_root_section(self):
        """ Return the root section """
        return self.sections.get(root=True)

    def render_story_structure(self, format='html'):
        """Render a representation of the Story structure"""
        output = []
        try:
            root = self.get_root_section()
        except Section.DoesNotExist:
            return ''

        output.append('<ul>')
        output.append(root.render(format))
        output.append('</ul>')
        return mark_safe(u'\n'.join(output))

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
    assets = models.ManyToManyField(Asset, related_name='sections',
                                    blank=True, through='SectionAsset')

    translated_fields = ['title']
    translation_set = 'sectiontranslation_set'

    def __unicode__(self):
        try:
            return self.title
        except IndexError:
            # HACK: Need this to support deleting Sections through
            # an inline on the Story Change page
            #
            # When deleting an object in the Django admin, a Section
            # object gets instantiated with no translation set.
            # So, the call to __getattr__() raises an IndexError
            return super(Section, self).__unicode__() 

    def render(self, format='html'):
        """Render a representation of the section structure"""
        try:
            return getattr(self, "render_" + format).__call__()
        except AttributeError:
            return self.__unicode__()

    def _child_relations(self):
        """Get a query set of through model instances for child sections"""
        return self.children.through.objects.filter(parent=self).order_by(
            'weight', 'child__sectiontranslation__title')

    def render_html(self):
        """Render a HTML representation of the section structure"""
        output = []
        output.append('<li class="section">')
        output.append("<h4>%s</h4>" % self.title)
        if self.assets.count() > 0:
            output.append("<h5>Assets</h5>")
            output.append("<ul>")
            for asset in self.assets.order_by('sectionasset__weight'):
                asset_title = asset.title
                if not asset_title:
                    asset_title = unicode(asset)
                output.append("<li>%s</li>" % asset_title)
            output.append("</ul>")

        if self.children.count():
            output.append("<ul>")
            for child_relation in self._child_relations():
                output.append(child_relation.child.render_html())
            output.append("</ul>")

        output.append("</li>")

        return mark_safe(u'\n'.join(output))

    def change_link(self):
        """Generate a link to the Django admin change page

        You can specify this in the Model Admin's readonly_fields or
        list_display options
        
        """
        if self.pk:
            change_url = urlresolvers.reverse(
                'admin:storybase_story_section_change', args=(self.pk,))
            return "<a href='%s'>Change Section</a>" % change_url
        else:
            return ''
    change_link.short_description = 'Change' 
    change_link.allow_tags = True

class SectionTranslation(TranslationModel):
    """Translated fields of a Section"""
    section = models.ForeignKey('Section')
    title = ShortTextField() 

    class Meta:
        """Model metadata options"""
        unique_together = (('section', 'language'))

    def __unicode__(self):
        return self.title

class SectionRelation(edge_factory(Section, concrete=False)):
    """Through class for parent/child relationships between sections"""
    weight = models.IntegerField(default=0)

class SectionAsset(models.Model):
    """Through class for Asset to Section relations"""
    section = models.ForeignKey('Section')
    asset = models.ForeignKey('storybase_asset.Asset')
    weight = models.IntegerField(default=0)

def add_section_asset_to_story(sender, instance, **kwargs):
    """When an asset is added to a Section, also add it to the Story
    
    Should be connected to SectionAsset's post_save signal.
    """
    if instance.asset not in instance.section.story.assets.all():
        # An asset was added to a section but it is not related to
        # the section's story.
        # Add it to the Story's list of assets.
        instance.section.story.assets.add(instance.asset)
        instance.section.story.save()

# Add assets to stories when they're added to sections
post_save.connect(add_section_asset_to_story, sender=SectionAsset)

def update_story_last_edited(sender, instance, **kwargs):
    """Update the a section's story's last edited field
    
    Should be connected to Section's post_save signal.
    """
    # Last edited is automatically set on save
    instance.story.save()

# Update a section's story's last edited field when the section is saved
post_save.connect(update_story_last_edited, sender=Section)

def create_story(title, summary='', language=settings.LANGUAGE_CODE, 
                 *args, **kwargs):
    """Convenience function for creating a Story

    Allows for the creation of stories without having to explicitly
    deal with the translations.

    """
    obj = Story(*args, **kwargs)
    obj.save()
    translation = StoryTranslation(story=obj, title=title, summary=summary,
                                   language=language)
    translation.save()
    return obj

def create_section(title, story, language=settings.LANGUAGE_CODE,
                   *args, **kwargs):
    """Convenience function for creating a Section

    Allows for the creation of a section without having to explicitly
    deal with the tranlsations.

    """
    obj = Section(story=story)
    obj.save()
    translation = SectionTranslation(section=obj, title=title, 
                                     language=language)
    translation.save()
    return obj
