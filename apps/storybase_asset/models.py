from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.safestring import mark_safe
from filer.fields.image import FilerImageField

ASSET_TYPES = (
  (u'article', u'article'),
  (u'image', u'image'),
  (u'map', u'map'),
)

class Asset(models.Model):
    caption = models.TextField(blank=True)
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    user = models.ForeignKey(User, related_name="assets")

    def __unicode__(self):
        return self.title

    def subclass(self):
        for attr in ('externalasset', 'htmlasset'):
            try:
                return getattr(self, attr)
            except ObjectDoesNotExist:
                pass

        return self 

    def render(self, format='html'):
        try:
            return getattr(self, "render_" + format).__call__()
        except AttributeError:
            return self.__unicode__()

class ExternalAsset(Asset):
    url = models.URLField()

    def render_html(self):
        output = []
        if self.type == 'image':
            output.append('<figure>')
            output.append('<img src="%s" alt="%s" />' % (self.url, self.title))
            if self.caption:
                output.append('<figcaption>')
                output.append(self.caption)
                output.append('</figcaption>')
            output.append('</figure>')
        else:
            output.append("<a href=\"%s\">%s</a>" % (self.url, self.title))

        return mark_safe(u'\n'.join(output))

class HtmlAsset(Asset):
    body = models.TextField(blank=True)

    def render_html(self):
        output = []
        if self.type == 'map':
            output.append('<figure>')
            output.append(self.body)
            if self.caption:
                output.append('<figcaption>')
                output.append(self.caption)
                output.append('</figcaption>')
            output.append('</figure>')
        else:
            output.append(self.body)
            
        return mark_safe(u'\n'.join(output))

class FilerImageAsset(Asset):
    image = FilerImageField()
