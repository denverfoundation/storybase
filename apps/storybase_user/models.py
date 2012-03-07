from django.contrib.auth.models import User
from django.db import models

class Organization(models.Model):
    """ An organization or a community group that users and stories can be associated with. """
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    members = models.ManyToManyField(User, related_name='organizations', blank=True)

class Project(models.Model):
    """ 
    A project that collects related stories.  
    
    Users can also be related to projects.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    members = models.ManyToManyField(User, related_name='projects', blank=True) 
