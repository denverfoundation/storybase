from django.contrib.auth.models import User
from django.db import models

ASSET_TYPES = (
  (u'article', u'article'),
)

class Asset(models.Model):
    caption = models.TextField(blank=True)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    user = models.ForeignKey(User, related_name="assets")

    def __unicode__(self):
        return self.title

class ExternalAsset(Asset):
    url = models.URLField()
