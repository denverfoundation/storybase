from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from uuidfield.fields import UUIDField
from storybase.fields import ShortTextField
from storybase.models import TranslatedModel, TranslationModel
from storybase.utils import slugify

class Organization(TranslatedModel):
    """ An organization or a community group that users and stories can be associated with. """
    organization_id = UUIDField(auto=True)
    website_url = models.URLField(blank=True)
    members = models.ManyToManyField(User, related_name='organizations', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    translated_fields = ['name', 'description', 'slug']

    translation_set = 'organizationtranslation_set'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('organization_detail', [self.organization_id])

class OrganizationTranslation(TranslationModel):
    organization = models.ForeignKey('Organization')
    name = ShortTextField()
    slug = models.SlugField()
    description = models.TextField(blank=True)


    class Meta:
        unique_together = (('organization', 'language'))

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ Overriding save to automatically set slug """
        if not self.slug:
            self.slug = slugify(self.name)
        super(OrganizationTranslation, self).save(*args, **kwargs)

class Project(TranslatedModel):
    """ 
    A project that collects related stories.  
    
    Users can also be related to projects.
    """
    project_id = UUIDField(auto=True)
    website_url = models.URLField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    organizations = models.ManyToManyField(Organization, related_name='projects', blank=True)
    members = models.ManyToManyField(User, related_name='projects', blank=True) 
    curated_stories = models.ManyToManyField('storybase_story.Story', related_name='curated_in_projects', blank=True, through='ProjectStory')

    translated_fields = ['name', 'description', 'slug']
    #translations = models.ManyToManyField('ProjectTranslation', blank=True, verbose_name=_('translations'))

    translation_set = 'projecttranslation_set'

    def __unicode__(self):
        return self.name

    def ordered_stories(self):
        """ Return sorted curated stories

        This is a helper method to make it easy to access a sorted 
        list of stories associated with the project in a template.

        Sorts first by weight, then by when a story was associated with
        the project.

        """
        return self.curated_stories.order_by('projectstory__weight', 'projectstory__added')

class ProjectTranslation(TranslationModel):
    project = models.ForeignKey('Project')
    name = ShortTextField()
    slug = models.SlugField()
    description = models.TextField(blank=True)

    class Meta:
        unique_together = (('project', 'language'))

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ Overriding save to automatically set slug """
        if not self.slug:
            self.slug = slugify(self.name)
        super(ProjectTranslation, self).save(*args, **kwargs)

class ProjectStory(models.Model):
    """ "Through" class for Project to Story relations """
    project = models.ForeignKey('Project')
    story = models.ForeignKey('storybase_story.Story')
    weight = models.IntegerField(default=0)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "story"

@receiver(post_save, sender=Project)
def add_story(sender, instance, **kwargs):
    """ Add stories in curated stories list to stories list if they're not already there """ 
    for story in instance.curated_stories.all():
        if instance not in story.projects.all():
            story.projects.add(instance)
            story.save()
