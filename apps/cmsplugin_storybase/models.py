from django.db import models
from cms.models.pluginmodel import CMSPlugin
from storybase_story.models import Story

class StoryPlugin(CMSPlugin):
    story = models.ForeignKey(Story, related_name='plugins')

    def __unicode__(self):
        return self.story.title
