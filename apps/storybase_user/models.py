"""Models representing people or groups of people"""

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from uuidfield.fields import UUIDField

from storybase.fields import ShortTextField
from storybase.models import (TimestampedModel, TranslatedModel,
                              TranslationModel)
    
from storybase.utils import slugify

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

class Organization(TranslatedModel, TimestampedModel):
    """ An organization or a community group that users and stories can be associated with. """
    organization_id = UUIDField(auto=True)
    slug = models.SlugField(blank=True)
    website_url = models.URLField(blank=True)
    members = models.ManyToManyField(User, related_name='organizations', blank=True)
    curated_stories = models.ManyToManyField('storybase_story.Story', related_name='curated_in_organizations', blank=True, through='OrganizationStory')

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
        instance.organization.slug = slugify(instance.name)
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

class Project(TranslatedModel, TimestampedModel):
    """ 
    A project that collects related stories.  
    
    Users can also be related to projects.
    """
    project_id = UUIDField(auto=True)
    slug = models.SlugField(blank=True)
    website_url = models.URLField(blank=True)
    organizations = models.ManyToManyField(Organization, related_name='projects', blank=True)
    members = models.ManyToManyField(User, related_name='projects', blank=True) 
    curated_stories = models.ManyToManyField('storybase_story.Story', related_name='curated_in_projects', blank=True, through='ProjectStory')

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
        instance.project.slug = slugify(instance.name)
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
