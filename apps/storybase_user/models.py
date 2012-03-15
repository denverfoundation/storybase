from django.contrib.auth.models import User
from django.db import models
from uuidfield.fields import UUIDField
from storybase.fields import ShortTextField

class Organization(models.Model):
    """ An organization or a community group that users and stories can be associated with. """
    organization_id = UUIDField(auto=True)
    name = ShortTextField()
    slug = models.SlugField()
    website_url = models.URLField()
    members = models.ManyToManyField(User, related_name='organizations', blank=True)

    def __unicode__(self):
        return self.name

class Project(models.Model):
    """ 
    A project that collects related stories.  
    
    Users can also be related to projects.
    """
    project_id = UUIDField(auto=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    members = models.ManyToManyField(User, related_name='projects', blank=True) 

    def __unicode__(self):
        return self.name
