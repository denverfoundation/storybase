from django.db import models
from apps.storybase_story.models import Story


class Badge(models.Model):
    """
    A badge can be added to
    """
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    icon_uri = models.URLField()

    stories = models.ManyToManyField(Story, related_name='badges')
