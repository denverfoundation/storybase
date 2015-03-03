
from django.db import models


class BadgeEditor(object):
    
    def can_edit_badge(self, badge):
        return badge in self.badges.all()


class Badge(models.Model):
    """
    A badge can be added to stories by users. Right now not all users
    can add all badges. So a badge has a list of stories it was added to
    and a list of users who can add it or remove it from stories.

    """
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    icon_uri = models.URLField()

    def __unicode__(self):
        return self.name
