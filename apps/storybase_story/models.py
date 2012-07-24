"""Models for stories and story sections"""

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.db import models
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_dag.models import edge_factory, node_factory

from uuidfield.fields import UUIDField

from storybase.fields import ShortTextField
from storybase.models import (LicensedModel, PermissionMixin, 
    PublishedModel, TimestampedModel, TranslatedModel, TranslationModel,
    set_date_on_published)
from storybase.utils import slugify
from storybase_asset.models import Asset, DataSet
from storybase_help.models import Help
from storybase_user.models import Organization, Project
from storybase_story import structure
from storybase_story.managers import StoryManager


class StoryPermission(PermissionMixin):
    """Permissions for the Story model"""
    def user_can_change(self, user):
        from storybase_user.utils import is_admin

        if not user.is_active:
            return False

        if self.author == user:
            return True

        if is_admin(user):
            return True

        return False

    def user_can_add(self, user):
        if user.is_active:
            return True

        return False

    def user_can_delete(self, user):
        return self.user_can_change(user)


class StoryTranslation(TranslationModel):
    """Encapsulates translated fields of a Story"""
    story = models.ForeignKey('Story')
    title = ShortTextField(blank=True) 
    summary = models.TextField(blank=True)
    call_to_action = models.TextField(_("Call to Action"),
                                      blank=True)

    class Meta:
        """Model metadata options"""
        unique_together = (('story', 'language'))

    def __unicode__(self):
        return self.title


class Story(TranslatedModel, LicensedModel, PublishedModel, 
            TimestampedModel, StoryPermission):
    """Metadata for a story

    The Story model stores a story's metadata and aggregates a story's
    media assets

    """
    story_id = UUIDField(auto=True)
    slug = models.SlugField(blank=True)
    byline = models.TextField()
    structure_type = models.CharField(_("structure"), max_length=20,
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
    datasets = models.ManyToManyField(DataSet, related_name='stories',
                                      blank=True)
    featured_assets = models.ManyToManyField(Asset,
       related_name='featured_in_stories', blank=True,
       help_text=_("Assets to be displayed in teaser version of Story"))
    organizations = models.ManyToManyField(Organization,
                                           related_name='stories',
                                           blank=True)
    projects = models.ManyToManyField(Project, related_name='stories',
                                      blank=True)
    is_template = models.BooleanField(_("Story is a template"),
                                      default=False)
    on_homepage = models.BooleanField(_("Featured on homepage"),
                                      default=False)
    contact_info = models.TextField(_("Contact Information"),
                                    blank=True)
    topics = models.ManyToManyField('storybase_taxonomy.Category',
                                    verbose_name=_("Topics"),
                                    related_name='stories',
                                    blank=True)
    locations = models.ManyToManyField('storybase_geo.Location',
                                       verbose_name=_("Locations"),
                                       related_name='stories',
                                       blank=True)
    places = models.ManyToManyField('storybase_geo.Place',
                                       verbose_name=_("Places"),
                                       related_name='stories',
                                       blank=True)

    objects = StoryManager()

    translated_fields = ['title', 'summary', 'call_to_action']
    translation_set = 'storytranslation_set'
    translation_class = StoryTranslation

    _structure_obj = None

    class Meta:
        """Model metadata options"""
        verbose_name_plural = "stories"

    def get_structure_obj(self):
        """Return a structure object for the story"""
        if self._structure_obj is None:
            # A structure object hasn't been instantiated yet.
            # Create one.
            structure_class = structure.manager.get_structure_class(
                self.structure_type)
            self._structure_obj = structure_class.__call__(story=self)

        return self._structure_obj
    structure = property(get_structure_obj)

    def __unicode__(self):
        if self.title:
            return self.title

        return _("Untitled Story") + " " + self.story_id

    @models.permalink
    def get_absolute_url(self):
        """Calculate the canonical URL for a Story"""
        if self.slug:
            return ('story_detail', [self.slug])

        return ('story_detail', [self.story_id])

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
        contributor_name = "" 
        if contributor.is_active and contributor.first_name:
            contributor_name = contributor.first_name 
                                
            if contributor.last_name:
                contributor_name = "%s %s." % (contributor.first_name,
                                               contributor.last_name[0])
            else:
                contributor_name = contributor.first_name

        return contributor_name

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

    def get_explore_url(self, filters=None):
        """
	Get a URL pointing to the explore view with specific filters set
	"""
	url = urlresolvers.reverse('explore_stories')
	qs_params = []
	for filter, values in filters.items():
	    if values:
	        qs_params.append("%s=%s" % (filter, ",".join([str(value) for value in values])))

        url += "?" + "&".join(qs_params) 
	return url
	
    def topics_with_links(self):
        """
        Return topics with links to the explore view with filters set
        to that topic

        """
        # This is a little kludgy and it seems to be cleaner to just 
        # handle this in a ``get_absolute_url`` method of the 
        # ``Category`` model.  However, I wanted to keep the knowledge of 
        # the explore view decoupled from the Categories model in case we 
        # want to use Categories for categorizing things other than stories.
        topics = [{'name': topic.name, 'url': self.get_explore_url({'topics': [topic.pk]})} for topic in self.topics.all()]
        return topics

    @property
    def inherited_places(self):
        """Get places related to this story, including parents"""
        inherited_places = set()
        for place in self.places.all():
            inherited_places.add(place)
            inherited_places.update(place.ancestors_set())
        return inherited_places

    @property
    def points(self):
        """
        Get points (longitude, latitude pairs) related to the story
        
        If the story has locations related with the story, use those,
        otherwise try to find centroids of related places.

        """
        points = []
        if self.locations.count():
            points = [(loc.lat, loc.lng) for loc in self.locations.all()]
        elif self.places.count():
            # We need to track the geolevel of the first place we've found
            # with a boundary so we can try to add points for all other
            # places at that geolevel
            point_geolevel = None
            # Loop through related places looking at smaller geographies 
            # first
            for place in self.places.all().order_by('-geolevel__level'):
                if place.boundary:
                    # Place has a geometry associated with it
                    centroid = place.boundary.centroid
                    if not point_geolevel:
                        points.append((centroid.y, centroid.x))
                        point_geolevel = place.geolevel
                    else:
                        if place.geolevel == point_geolevel:
                            points.append((centroid.y, centroid.x))
                        else:
                            # We've exhausted all the points at the 
                            # lowest geolevel.  Quit.
                            break

            # TODO: Decide if we should check non-explicit places

        return points



def set_story_slug(sender, instance, **kwargs):
    """
    When a StoryTranslation is saved, set its Story's slug if it doesn't have 
    one
    
    Should be connected to StoryTranslation's post_save signal.
    """
    try:
        if not instance.story.slug:
            instance.story.slug = slugify(instance.title)
        instance.story.save()
    except Story.DoesNotExist:
        # Instance doesn't have a related story.
        # Encountered this when loading fixture
        pass


def update_last_edited(sender, instance, **kwargs):
    """
    When an object is added to a Story, update the related object's
    last edited field.
    """
    action = kwargs.get('action')
    pk_set = kwargs.get('pk_set')
    model = kwargs.get('model')
    reverse = kwargs.get('reverse')
    if action in ("post_add", "post_remove") and pk_set and not reverse:
        for obj in model.objects.filter(pk__in=pk_set):
            obj.last_edited = datetime.now()
            obj.save()


# Hook up some signal handlers
pre_save.connect(set_date_on_published, sender=Story)
post_save.connect(set_story_slug, sender=StoryTranslation)
m2m_changed.connect(update_last_edited, sender=Story.organizations.through)
m2m_changed.connect(update_last_edited, sender=Story.projects.through)


class SectionPermission(PermissionMixin):
    """Permissions for the Section model"""
    def user_can_change(self, user):
        from storybase_user.utils import is_admin

        if not user.is_active:
            return False

        if self.story.author == user:
            return True

        if is_admin(user):
            return True

        return False

    def user_can_add(self, user):
        return self.user_can_change(user)

    def user_can_delete(self, user):
        return self.user_can_change(user)


class SectionTranslation(TranslationModel):
    """Translated fields of a Section"""
    section = models.ForeignKey('Section')
    title = ShortTextField() 

    class Meta:
        """Model metadata options"""
        unique_together = (('section', 'language'))

    def __unicode__(self):
        return self.title


class Section(node_factory('SectionRelation'), TranslatedModel, SectionPermission):
    """ Section of a story """
    section_id = UUIDField(auto=True)
    story = models.ForeignKey('Story', related_name='sections')
    # True if this section the root section of the story, either
    # the first section in a linear story, or the central node
    # in a drill-down/"spider" structure.  Otherwise, False
    root = models.BooleanField(default=False)
    weight = models.IntegerField(default=0)
    layout = models.ForeignKey('SectionLayout', null=True)
    help = models.ForeignKey(Help, null=True)
    """The ordering of top-level sections relative to each other"""
    assets = models.ManyToManyField(Asset, related_name='sections',
                                    blank=True, through='SectionAsset')

    translated_fields = ['title']
    translation_set = 'sectiontranslation_set'
    translation_class = SectionTranslation

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

    def is_island(self):
        """
        Check if has no ancestors nor children

        This is a patch for a broken implementation in django_dag.  
        """
        # TODO: Remove this when django_dag is fixed.
        # See https://github.com/elpaso/django-dag/pull/4
        return bool(not self.children.count() and not self.ancestors_set())

    def child_relations(self):
        """
        Get a query set of through model instances for children
        of this section
        """
        return self.children.through.objects.filter(parent=self).order_by(
            'weight', 'child__sectiontranslation__title')

    def get_next_section(self):
        """Get the next section"""
        return self.story.structure.get_next_section(self)

    def get_previous_section(self):
        """Get the previous section"""
        return self.story.structure.get_previous_section(self)

    def render(self, format='html'):
        """Render a representation of the section structure"""
        try:
            return getattr(self, "render_" + format).__call__()
        except AttributeError:
            return self.__unicode__()

    def to_simple(self):
        """
        Return a simplified representation of this object for serialization
        """
        simple = {
            'section_id': self.section_id,
            'title': self.title,
            'children': []
        }
        next_section = self.get_next_section()
        previous_section = self.get_previous_section()
        if next_section:
            simple.update({'next_section_id': next_section.section_id})
        if previous_section:
            simple.update(
                {'previous_section_id': previous_section.section_id})
        for child_relation in self.child_relations():
            simple['children'].append(child_relation.child.section_id)
        
        return simple

    def render_html(self):
        """Render a HTML representation of the section structure"""
        output = []
        context = {
            'asset_content': {}
        }
        output.append("<h2 class='title'>%s</h2>" % self.title)
        template_filename = self.layout.get_template_filename()
        for asset in self.assets.select_subclasses():
            section_asset = asset.sectionasset_set.get(section=self)
            context['asset_content'][section_asset.container.name] = asset.render_html()

        output.append(render_to_string(template_filename, context))
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



class SectionRelation(edge_factory(Section, concrete=False)):
    """Through class for parent/child relationships between sections"""
    weight = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s is child of %s" % (self.child, self.parent)


class SectionAssetPermission(PermissionMixin):
    """Permissions for the SectionAsset model"""
    def user_can_change(self, user):
        from storybase_user.utils import is_admin

        if not user.is_active:
            return False

        if self.section.story.author == user:
            return True

        if is_admin(user):
            return True

        return False

    def user_can_add(self, user):
        return self.user_can_change(user)

    def user_can_delete(self, user):
        return self.user_can_change(user)


class SectionAsset(models.Model, SectionAssetPermission):
    """Through class for Asset to Section relations"""
    section = models.ForeignKey('Section')
    asset = models.ForeignKey('storybase_asset.Asset')
    container = models.ForeignKey('Container', null=True)


def add_section_asset_to_story(sender, instance, **kwargs):
    """When an asset is added to a Section, also add it to the Story
    
    Should be connected to SectionAsset's post_save signal.
    """
    try:
        if instance.asset not in instance.section.story.assets.all():
            # An asset was added to a section but it is not related to
            # the section's story.
            # Add it to the Story's list of assets.
            instance.section.story.assets.add(instance.asset)
            instance.section.story.save()
    except Asset.DoesNotExist:
        # Instance doesn't have a related asset.
        # Encountered when loading fixture
        pass

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

class StoryTemplateTranslation(TranslationModel):
    """Translatable fields for the StoryTemplate model"""
    story_template = models.ForeignKey('StoryTemplate')
    title = ShortTextField()
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title


class StoryTemplate(TranslatedModel):
    """Metadata for a template used to create new stories"""
    TIME_NEEDED_CHOICES = (
        ('5 minutes', _('5 minutes')),
        ('30 minutes', _('30 minutes')),
    )
    
    template_id = UUIDField(auto=True)
    # The structure of the template comes from a story model instance
    story = models.ForeignKey('Story', blank=True, null=True)
    # The amount of time needed to create a story of this type
    time_needed = models.CharField(max_length=140, choices=TIME_NEEDED_CHOICES,
                                   blank=True)

    # Class attributes to handle translation
    translated_fields = ['title', 'description']
    translation_set = 'storytemplatetranslation_set'
    translation_class = StoryTemplateTranslation

    def __unicode__(self):
        return self.title


class SectionLayoutTranslation(TranslationModel):
    """Translatable fields for the SectionLayout model"""
    layout = models.ForeignKey('SectionLayout')
    name = ShortTextField()

    def __unicode__(self):
        return self.name


class SectionLayout(TranslatedModel):
    TEMPLATE_CHOICES = [(name, name) for name 
                        in settings.STORYBASE_LAYOUT_TEMPLATES]

    layout_id = UUIDField(auto=True)
    template = models.CharField(_("template"), max_length=100, choices=TEMPLATE_CHOICES)
    containers = models.ManyToManyField('Container', related_name='layouts',
                                        blank=True)

    # Class attributes to handle translation
    translated_fields = ['name']
    translation_set = 'sectionlayouttranslation_set'
    translation_class = SectionLayoutTranslation

    def __unicode__(self):
        return self.name

    def get_template_filename(self):
        return "storybase_story/sectionlayouts/%s" % (self.template)

    def get_template_contents(self):
        template_filename = self.get_template_filename() 
        return render_to_string(template_filename)


class Container(models.Model):
    """
    A space to put assets within a ``TemplateLayout`` 
    """
    name = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name
    

# Internal API functions for creating model instances in a way that
# abstracts out the translation logic a bit.

def create_story(title, structure_type=structure.DEFAULT_STRUCTURE,
                 summary='', call_to_action='',
                 language=settings.LANGUAGE_CODE, 
                 *args, **kwargs):
    """Convenience function for creating a Story

    Allows for the creation of stories without having to explicitly
    deal with the translations.

    """
    obj = Story(structure_type=structure_type, *args, **kwargs)
    obj.save()
    translation = StoryTranslation(story=obj, title=title, summary=summary,
                                   call_to_action=call_to_action,
                                   language=language)
    translation.save()
    return obj

def create_section(title, story, layout=None,
                   language=settings.LANGUAGE_CODE, *args, **kwargs):
    """Convenience function for creating a Section

    Allows for the creation of a section without having to explicitly
    deal with the tranlsations.

    """
    obj = Section(story=story, layout=layout, *args, **kwargs)
    obj.save()
    translation = SectionTranslation(section=obj, title=title, 
                                     language=language)
    translation.save()
    return obj
