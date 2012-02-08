from django.db import models
from cms.models.pluginmodel import CMSPlugin

class StoryPlugin(CMSPlugin):
    story = models.ForeignKey('storybase_story.Story', related_name='plugins')

    def __unicode__(self):
        return self.story.title
