from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField
from uuidfield.fields import UUIDField
from storybase.models import TranslatedModel, TranslationModel

ASSET_TYPES = (
  (u'article', u'article'),
  (u'image', u'image'),
  (u'map', u'map'),
)

class Asset(TranslatedModel):
    asset_id = UUIDField(auto=True)
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    owner = models.ForeignKey(User, related_name="assets")

    translated_fields = ['title', 'caption']

    def __unicode__(self):
        return self.title

    def subclass(self):
        for attr in ('externalasset', 'htmlasset', 'filerimageasset'):
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


class AssetTranslation(TranslationModel):
    asset = models.ForeignKey('Asset', related_name="%(app_label)s_%(class)s_related") 
    title = models.CharField(max_length=200)
    caption = models.TextField(blank=True)

    class Meta:
        abstract = True
        unique_together = (('asset', 'language')) 

class ExternalAsset(Asset):
    translations = models.ManyToManyField('ExternalAssetTranslation', blank=True, verbose_name=_('translations'))

    translation_set = 'storybase_asset_externalassettranslation_related'
    translated_fields = Asset.translated_fields + ['url']

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

class ExternalAssetTranslation(AssetTranslation):
    url = models.URLField()

class HtmlAsset(Asset):
    translations = models.ManyToManyField('HtmlAssetTranslation', blank=True, verbose_name=_('translations'))

    translation_set = 'storybase_asset_htmlassettranslation_related'
    translated_fields = Asset.translated_fields + ['body']

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

class HtmlAssetTranslation(AssetTranslation):
    body = models.TextField(blank=True)

class FilerImageAsset(Asset):
    translations = models.ManyToManyField('FilerImageAssetTranslation', blank=True, verbose_name=_('translations'))

    translation_set = 'storybase_asset_filerimageassettranslation_related'
    translated_fields = Asset.translated_fields + ['image']

    def render_html(self):
        output = []
        output.append('<figure>')
        output.append('<img src="%s" alt="%s" />' % (self.image.url, self.title))
        if self.caption:
            output.append('<figcaption>')
            output.append(self.caption)
            output.append('</figcaption>')
        output.append('</figure>')
            
        return mark_safe(u'\n'.join(output))

class FilerImageAssetTranslation(AssetTranslation):
    image = FilerImageField()
