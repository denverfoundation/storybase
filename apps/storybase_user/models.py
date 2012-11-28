"""Models representing people or groups of people"""

try:
    import shortuuid
    import uuid
except ImportError:
    shortuuid = None

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from uuidfield.fields import UUIDField

from storybase.fields import ShortTextField
from storybase.managers import FeaturedManager
from storybase.models import (TimestampedModel, TranslatedModel,
                              TranslationModel)
from storybase.utils import unique_slugify
from storybase_asset.models import FeaturedAssetsMixin

ADMIN_GROUP_NAME = getattr(settings, 'ADMIN_GROUP_NAME', 'CA Admin')
"""Default name of the administrator group"""

class CuratedStory(models.Model):
    """ Abstract base class for "through" model for associating Stories with Projects and Organizations """
    story = models.ForeignKey('storybase_story.Story')
    weight = models.IntegerField(default=0)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = "story"


class FeaturedStoriesMixin(object):
    """
    Mixin that provides some utility methods for populating the
    featured stories sections of templates
    """
    def get_featured_queryset(self):
        return self.curated_stories.all()

    def featured_story(self):
        try:
            return self.get_featured_queryset().order_by('-last_edited')[0]
        except IndexError:
            return None


class StoriesMixin(object):
    """
    Mixin that provides some utility methods for populating the
    stories section of templates

    This provides a common interface for templates to access a model
    instance's stories, even when they may be accessed through different
    model fields.

    """
    def get_stories_queryset(self):
        return self.stories.filter(status='published')

    def all_stories(self):
        return self.get_stories_queryset().order_by('-last_edited')


class RecentStoriesMixin(StoriesMixin):
    """
    Mixin that provides some utility methods for populating the recent
    stories section of templates

    This provides a common interface for templates to access a model
    instance's stories, even when they may be accessed through different
    model fields.

    """
    def get_recent_queryset(self):
        return self.get_stories_queryset()

    def recent_stories(self, count=3):
        return self.get_recent_queryset().order_by('-last_edited')[:count]
        

class Organization(FeaturedAssetsMixin, RecentStoriesMixin,
                   FeaturedStoriesMixin, TranslatedModel, TimestampedModel):
    """ An organization or a community group that users and stories can be associated with. """
    organization_id = UUIDField(auto=True, db_index=True)
    slug = models.SlugField(blank=True)
    website_url = models.URLField(blank=True)
    members = models.ManyToManyField(User, related_name='organizations', blank=True)
    curated_stories = models.ManyToManyField('storybase_story.Story', related_name='curated_in_organizations', blank=True, through='OrganizationStory')
    on_homepage = models.BooleanField(_("Featured on homepage"),
		                      default=False)
    featured_assets = models.ManyToManyField('storybase_asset.Asset',
       related_name='featured_in_organizations', blank=True,
       help_text=_("Assets to be displayed in teaser version of this Organization"))

    objects = FeaturedManager()

    translated_fields = ['name', 'description']
    translation_set = 'organizationtranslation_set'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('organization_detail', [self.slug])

    def add_story(self, story, weight=0):
        """ Associate a story with the Organization 
        
        Arguments:
        story -- The Story model instance object to be associated
        weight -- The ordering of the story relative to other stories

        """
        OrganizationStory.objects.create(organization=self, story=story,
                                         weight=weight)

    def ordered_stories(self):
        """ Return sorted curated stories

        This is a helper method to make it easy to access a sorted 
        list of stories associated with the project in a template.

        Sorts first by weight, then by when a story was associated with
        the project in reverse chronological order.

        """
        return self.curated_stories.order_by('organizationstory__weight', '-organizationstory__added')

    def get_default_img_url_choices(self):
        return settings.STORYBASE_DEFAULT_ORGANIZATION_IMAGES


class OrganizationTranslation(TranslationModel, TimestampedModel):
    organization = models.ForeignKey('Organization')
    name = ShortTextField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = (('organization', 'language'))

    def __unicode__(self):
        return self.name

def set_organization_slug(sender, instance, **kwargs):
    """
    When an OrganizationTranslation is saved, set its Organization's slug if it
    doesn't have one
    
    Should be connected to OrganizationTranslation's post_save signal.
    """
    if not instance.organization.slug:
        unique_slugify(instance.organization, instance.name)
	instance.organization.save()

# Hook up some signal handlers
post_save.connect(set_organization_slug, sender=OrganizationTranslation)

class OrganizationStory(CuratedStory):
    """ "Through" class for Organization to Story relations """
    organization = models.ForeignKey('Organization')

@receiver(post_save, sender=Organization)
def add_story_to_organization(sender, instance, **kwargs):
    """ Add stories in curated stories list to stories list if they're not already there """ 
    for story in instance.curated_stories.all():
        if instance not in story.organizations.all():
            story.organizations.add(instance)
            story.save()

class Project(FeaturedAssetsMixin, RecentStoriesMixin, FeaturedStoriesMixin,
              TranslatedModel, TimestampedModel):
    """ 
    A project that collects related stories.  
    
    Users can also be related to projects.
    """
    project_id = UUIDField(auto=True, db_index=True)
    slug = models.SlugField(blank=True)
    website_url = models.URLField(blank=True)
    organizations = models.ManyToManyField(Organization, related_name='projects', blank=True)
    members = models.ManyToManyField(User, related_name='projects', blank=True) 
    curated_stories = models.ManyToManyField('storybase_story.Story', related_name='curated_in_projects', blank=True, through='ProjectStory')
    on_homepage = models.BooleanField(_("Featured on homepage"),
		                      default=False)
    featured_assets = models.ManyToManyField('storybase_asset.Asset',
       related_name='featured_in_projects', blank=True,
       help_text=_("Assets to be displayed in teaser version of this Project"))

    objects = FeaturedManager()

    translated_fields = ['name', 'description']
    translation_set = 'projecttranslation_set'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('project_detail', [self.slug])

    def add_story(self, story, weight=0):
        """ Associate a story with the Project 
        
        Arguments:
        story -- The Story model instance object to be associated
        weight -- The ordering of the story relative to other stories

        """
        ProjectStory.objects.create(project=self, story=story,
                                    weight=weight)

    def ordered_stories(self):
        """ Return sorted curated stories

        This is a helper method to make it easy to access a sorted 
        list of stories associated with the project in a template.

        Sorts first by weight, then by when a story was associated with
        the project in reverse chronological order.

        """
        return self.curated_stories.order_by('projectstory__weight', '-projectstory__added')

    def get_default_img_url_choices(self):
        return settings.STORYBASE_DEFAULT_PROJECT_IMAGES


class ProjectTranslation(TranslationModel):
    project = models.ForeignKey('Project')
    name = ShortTextField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = (('project', 'language'))

    def __unicode__(self):
        return self.name

def set_project_slug(sender, instance, **kwargs):
    """
    When an ProjectTranslation is saved, set its Project's slug if it
    doesn't have one
    
    Should be connected to ProjectTranslation's post_save signal.
    """
    if not instance.project.slug:
        unique_slugify(instance.project, instance.name)
	instance.project.save()

# Hook up some signal handlers
post_save.connect(set_project_slug, sender=ProjectTranslation)


class ProjectStory(CuratedStory):
    """ "Through" class for Project to Story relations """
    project = models.ForeignKey('Project')

@receiver(post_save, sender=Project)
def add_story_to_project(sender, instance, **kwargs):
    """ Add stories in curated stories list to stories list if they're not already there """ 
    for story in instance.curated_stories.all():
        if instance not in story.projects.all():
            story.projects.add(instance)
            story.save()


class UserProfile(RecentStoriesMixin, models.Model):
    user = models.OneToOneField(User)

    profile_id = UUIDField(auto=True, db_index=True)

    # Notification preferences
    # Right now these represent e-mail contact
    # Floodlight updates
    notify_updates = models.BooleanField("Floodlight Updates", default=True,
        help_text="Updates about new Floodlight features, events and storytelling tips")
    notify_admin = models.BooleanField("Administrative Updates",
        default=True,
        help_text="Administrative account updates")
    notify_digest = models.BooleanField("Monthly Digest", default=True,
        help_text="A monthly digest of featured Floodlight stories")
    # Notifications about my stories
    notify_story_featured = models.BooleanField("Homepage Notification",
        default=True,
        help_text="One of my stories is featured on the Floodlight homepage or newsletter")
    notify_story_comment = models.BooleanField("Comment Notification",
        default=True,
        help_text="Someone comments on one of my stories")

    def __unicode__(self):
        return unicode(self.user)

    @models.permalink
    def get_absolute_url(self):
        if shortuuid:
            profile_uuid = uuid.UUID(self.profile_id)
            return ('userprofile_detail', (), 
                    {'short_profile_id': shortuuid.encode(profile_uuid)})

        return ('userprofile_detail', (), 
                {'profile_id': self.profile_id})

    def name(self):
        # Import needs to go here to prevent a circular import
        from storybase_user.utils import format_user_name
        return format_user_name(self.user)

    def get_stories_queryset(self):
        return self.user.stories.filter(status='published')


def create_user_profile(sender, instance, created, **kwargs):
    """Signal handler for creating a profile on user account creation"""
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


def create_project(name, description='', website_url='', language=settings.LANGUAGE_CODE):
    """ Convenience function for creating a Project 
    
    Allows for the creation of stories without having to explicitely
    deal with the translations.

    """
    project = Project(website_url=website_url)
    project.save()
    project_translation = ProjectTranslation(
        name=name,
        description=description, 
        project=project)
    project_translation.save()
    return project

def create_organization(name, description='', website_url='', language=settings.LANGUAGE_CODE):
    """ Convenience function for creating an Organization
    
    Allows for the creation of organizations without having to explicitely
    deal with the translations.

    """
    org = Organization(website_url=website_url)
    org.save()
    org_translation = OrganizationTranslation(
        name=name,
        description=description,
        organization=org)
    org_translation.save()
    return org
