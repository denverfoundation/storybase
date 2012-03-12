from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext, ugettext_lazy as _
from django.utils import translation
from filer.fields.image import FilerImageField

ASSET_TYPES = (
  (u'article', u'article'),
  (u'image', u'image'),
  (u'map', u'map'),
)

class Asset(models.Model):
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    owner = models.ForeignKey(User, related_name="assets")

    translated_fields = ('title', 'caption',)
    _translation_cache = None

    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        self._translation_cache = {}

    def __getattribute__(self, name):
        """ Attribute getter that searches for fields on the translation model class

        This implementation is based on the one in django-mothertongue by 
        Rob Charlwood https://github.com/robcharlwood/django-mothertongue
        """
        get = lambda p:super(Asset, self).__getattribute__(p)
        translated_fields = get('translated_fields') 
        if name in translated_fields:
            try:
                translation_set = get('translation_set')
                code = translation.get_language()
                translated_manager = get(translation_set)
                try:
                    translated_object = None
                    translated_object = self._translation_cache[code]
                except KeyError:
                    try:
                        translated_object = translated_manager.get(language=code)
                    except ObjectDoesNotExist:
                        # If 'en-us' doesn't have a translation,
                        # try 'en'
                        new_code = code.split('-')[0]
                        translated_object = translated_manager.get(language=new_code)
                finally:
                    self._translation_cache[code] = translated_object
                if translated_object:
                    return getattr(translated_object, name)
            except (ObjectDoesNotExist, AttributeError):
                # If title attribute doesn't exist on the Asset model, 
                # try the subclass.
                if name == 'title':
                    return getattr(self.subclass(), name)

        return get(name)

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


class AssetTranslation(models.Model):
    asset = models.ForeignKey('Asset', related_name="%(app_label)s_%(class)s_related") 
    language = models.CharField(max_length=15, choices=settings.LANGUAGES)
    title = models.CharField(max_length=200)
    caption = models.TextField(blank=True)

    class Meta:
        abstract = True
        unique_together = (('asset', 'language')) 

class ExternalAsset(Asset):
    translations = models.ManyToManyField('ExternalAssetTranslation', blank=True, verbose_name=_('translations'))

    translation_set = 'storybase_asset_externalassettranslation_related'
    translated_fields = Asset.translated_fields + ('url',)

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
    translated_fields = Asset.translated_fields + ('body',)

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
    translated_fields = Asset.translated_fields + ('image',)

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
