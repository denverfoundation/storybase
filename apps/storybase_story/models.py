"""Models for stories and story sections"""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
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
from storybase_story.managers import StoryManager
from storybase_story import structure
#from storybase_tag.models import TaggedItem

class StoryTranslation(TranslationModel):
    """Encapsulates translated fields of a Story"""
    story = models.ForeignKey('Story')
    title = ShortTextField() 
    summary = models.TextField(blank=True)

    class Meta:
        """Model metadata options"""
        unique_together = (('story', 'language'))

    def __unicode__(self):
        return self.title


class Story(TranslatedModel, LicensedModel, PublishedModel, 
            TimestampedModel):
    """Metadata for a story

    The Story model stores a story's metadata and aggregates a story's
    media assets

    """
    story_id = UUIDField(auto=True)
    slug = models.SlugField(blank=True)
    byline = models.TextField()
    structure = models.CharField(max_length=20,
        choices=structure.manager.get_structure_options())
    # blank=True, null=True to bypass validation so the user doesn't
    # have to always remember to set this in the Django admin.
    # Though this is set to blank=True, null=True, we should always set
    # this value.  In fact, the StoryModelAdmin class sets this to
    # request.user
    author = models.ForeignKey(User, related_name="stories", blank=True,
                               null=True)
    assets = models.ManyToManyField(Asset, related_name='stories',
                                    blank=True)
    featured_assets = models.ManyToManyField(Asset,
       related_name='featured_in_stories', blank=True,
       help_text=_("Assets to be displayed in teaser version of Story"))
    organizations = models.ManyToManyField(Organization,
                                           related_name='stories',
                                           blank=True)
    projects = models.ManyToManyField(Project, related_name='stories',
                                      blank=True)
    on_homepage = models.BooleanField(_("Featured on homepage"),
		                      default=False)
    #tags = TaggableManager(through=TaggedItem, blank=True)

    objects = StoryManager()

    translated_fields = ['title', 'summary']
    translation_set = 'storytranslation_set'

    _structure_obj = None

    class Meta:
        """Model metadata options"""
        verbose_name_plural = "stories"

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        """Calculate the canonical URL for a Story"""
        return ('story_detail', [self.slug])

    def get_full_url(self):
        """
        Calculate the canonical URL for a Story, including its
        domain name.
        """
        return "http://%s%s" % (Site.objects.get_current().domain,
                                self.get_absolute_url())

    @property
    def contributor_name(self):
        """
        Return the contributor's first name and last initial or username
        """ 
        contributor = self.author
        contributor_name = contributor.username
        if contributor.first_name:
            contributor_name = contributor.first_name 
                                
            if contributor.last_name:
                contributor_name = "%s %s." % (contributor.first_name,
                                               contributor.last_name[0])
            else:
                contributor_name = contributor.first_name

        return contributor_name

    def get_structure_obj(self):
        """Return a structure object for the story"""
        if self._structure_obj is None:
            # A structure object hasn't been instantiated yet.
            # Create one.
            structure_class = structure.manager.get_structure_class(
            self.structure)
            self._structure_obj = structure_class.__call__(story=self)

        return self._structure_obj

    def sections_flat(self):
        """
        Return a list of sections ordered with each branch coming before
        the next
        """
        flattened = []
        for section in self.sections.filter(root=True).order_by('weight'):
            flattened.append(section)
            flattened = flattened + section.children_flat()

        return flattened

    def sections_json(self):
        """Return a JSON representation of the story sections"""
        sections = [] 
        for section in self.sections_flat():
            sections.append(section.to_simple())

        return mark_safe(simplejson.dumps(sections))

    def to_simple(self):
        """
        Return a simplified version of the story object that can be
        passed to json.dumps()
        """
        return {
            'story_id': self.story_id,
            'title': self.title,
            'summary': self.summary
        }

    def to_json(self):
        """Return JSON representation of this object"""
        return mark_safe(simplejson.dumps(self.to_simple())) 

    def render_featured_asset(self, format='html'):
        """Render a representation of the story's featured asset"""
        try:
            # Return the first featured asset.  We have the ability of 
            # selecting multiple featured assets.  Perhaps in the future
            # allow for specifying a particular feature asset or randomly
            # displaying one.
            featured_asset = self.featured_assets.select_subclasses()[0]
            thumbnail_options = {}
            if format == 'html':
                thumbnail_options.update({'html_class': 'featured-asset'})
            return featured_asset.render_thumbnail(format=format, 
                                                   **thumbnail_options)
        except IndexError:
            # No featured assets
            return '' 

    def featured_asset_thumbnail_url(self):
        """Return the URL of the featured asset's thumbnail

        Returns None if the asset cannot be converted to a thumbnail image.

        """
        try:
            featured_asset = self.featured_assets.select_subclasses()[0]
            return featured_asset.get_thumbnail_url()
        except IndexError:
            # No featured assets
            return None

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

    def render_toc(self, format='html'):
        """Render a representation of the Story's table of contents"""
        structure = self.get_structure_obj()
        return structure.render_toc(format)


def set_story_slug(sender, instance, **kwargs):
    """
    When a StoryTranslation is saved, set its Story's slug if it doesn't have 
    one
    
    Should be connected to StoryTranslation's post_save signal.
    """
    if not instance.story.slug:
        instance.story.slug = slugify(instance.title)
	instance.story.save()

# Hook up some signal handlers
pre_save.connect(set_date_on_published, sender=Story)
post_save.connect(set_story_slug, sender=StoryTranslation)

class Section(node_factory('SectionRelation'), TranslatedModel):
    """ Section of a story """
    section_id = UUIDField(auto=True)
    story = models.ForeignKey('Story', related_name='sections')
    # True if this section the root section of the story, either
    # the first section in a linear story, or the central node
    # in a drill-down/"spider" structure.  Otherwise, False
    root = models.BooleanField(default=False)
    weight = models.IntegerField(default=0)
    """The ordering of top-level sections relative to each other"""
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

    @property
    def sections_in_same_story(self):
        """Return other sections in the same story"""
        return self.__class__.objects.filter(story=self.story)

    def _child_relations(self):
        """
        Get a query set of through model instances for children
        of this section
        """
        return self.children.through.objects.filter(parent=self).order_by(
            'weight', 'child__sectiontranslation__title')

    def _parent_relations(self):
        """
        Get a list of through model instances for parents of this 
        section
        """
        # This is a little confusing because we want parents, not
        # children.  self.children.through just gets us the "through" class
        # for the relation.
        return self.children.through.objects.filter(child=self).order_by(
            'weight', 'child__sectiontranslation__title')

    # TODO: Think about the best strategy for building a sense of
    # previous and next sections. I'm not sure if this is the best
    # place for the functionality and there's likely a way to avoid
    # having to traverse the tree so many times.

    def _next_child_section(self):
        """Return the first section that is a child of this section"""
        # We get it through the "through" class so we can order
        # the children by weight
        relation = self._child_relations()[0]
        return relation.child

    def _next_root_section(self):
        """Return the next top-level section"""
        if self.is_root() or self.is_island():
            root = self
        else:
            root = self.get_roots()[0]

        found = False
        for section in self.sections_in_same_story.order_by('weight'):
            if found:
                if section.is_root() or section.is_island():
                    return section
            else:
                if section == root:
                    found = True

        return None

    def get_next_section(self):
        """Get the next section"""
        # TODO: Unit test for this
        if self.children.count():
            # The section has children, return the first child
            section = self._next_child_section()
        else:
            # The section is a leaf or island
            section = self._next_root_section()
           
        return section

    def _previous_parent_section(self):
        # We get it through the "through" class so we can order
        # the parents by weight
        relation = self._parent_relations()[0]
        return relation.parent

    def _previous_root_section(self):
        if self.is_root() or self.is_island():
            root = self
        else:
            root = self.get_roots()[0]

        found = False
        for section in self.sections_in_same_story.order_by('-weight'):
            if found:
                if section.is_root() or section.is_island():
                    return section
            else:
                if section == root:
                    found = True

        return None

    def get_previous_section(self):
        """Get the previous section"""
        # TODO: Unit test for this
        if self.ancestors_set():
            # The section has ancestors.  Return the first one.
            section = self._previous_parent_section()
        else:
            # The section is a root or an island
            section = self._previous_root_section()

        return section

    def render(self, format='html'):
        """Render a representation of the section structure"""
        try:
            return getattr(self, "render_" + format).__call__()
        except AttributeError:
            return self.__unicode__()


    def children_flat(self):
        """
        Return a list of child sections ordered with each branch
        coming before the next
        """
        flattened = []
        for relation in self._child_relations():
            flattened.append(relation.child)
            flattened = flattened + relation.child.children_flat()
        return flattened

    def to_simple(self):
        """
        Return a simplified representation of this object for serialization
        """
        simple = {
            'section_id': self.section_id,
            'title': self.title
        }
        next_section = self.get_next_section()
        previous_section = self.get_previous_section()
        if next_section:
            simple.update({'next_section_id': next_section.section_id})
        if previous_section:
            simple.update(
                {'previous_section_id': previous_section.section_id})
        
        return simple

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

def create_story(title, structure=structure.DEFAULT_STRUCTURE, summary='', 
                 language=settings.LANGUAGE_CODE, 
                 *args, **kwargs):
    """Convenience function for creating a Story

    Allows for the creation of stories without having to explicitly
    deal with the translations.

    """
    obj = Story(structure=structure, *args, **kwargs)
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
    obj = Section(story=story, *args, **kwargs)
    obj.save()
    translation = SectionTranslation(section=obj, title=title, 
                                     language=language)
    translation.save()
    return obj
