from django.contrib.auth.models import User
from django.db import models

ASSET_TYPES = (
  (u'article', u'article'),
  (u'map', u'map'),
)

class Asset(models.Model):
    caption = models.TextField(blank=True)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    user = models.ForeignKey(User, related_name="assets")

    def __unicode__(self):
        return self.title

    def render(self, format='html'):
        try:
            return getattr(self, "render_" + format).__call__()
        except AttributeError:
            return self.__unicode__()

class ExternalAsset(Asset):
    url = models.URLField()

    def render_html(self):
        return "<a href=\"%s\">%s</a>" % (self.url, self.title)

class HtmlAsset(Asset):
    body = models.TextField(blank=True)

    def render_html(self):
        return self.body
