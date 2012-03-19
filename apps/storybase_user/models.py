from django.contrib.auth.models import User
from django.db import models
from uuidfield.fields import UUIDField
from storybase.fields import ShortTextField
from storybase.models import TranslatedModel, TranslationModel

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

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('organization', 'language'))

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
    # TODO: Add Stories field to Project 

    translated_fields = ['name', 'description', 'slug']
    #translations = models.ManyToManyField('ProjectTranslation', blank=True, verbose_name=_('translations'))

    translation_set = 'projecttranslation_set'

    def __unicode__(self):
        return self.name

class ProjectTranslation(TranslationModel):
    project = models.ForeignKey('Project')
    name = ShortTextField()
    slug = models.SlugField()
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('project', 'language'))
