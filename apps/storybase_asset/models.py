from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from filer.fields.image import FilerImageField
from model_utils.managers import InheritanceManager
import oembed
from oembed.exceptions import OEmbedMissingEndpoint
from uuidfield.fields import UUIDField
from storybase.fields import ShortTextField
from storybase.models import (LICENSES, DEFAULT_LICENSE,
    get_license_name,
    TranslatedModel, TranslationModel)

oembed.autodiscover()

ASSET_TYPES = (
  (u'image', u'image'),
  (u'audio', u'audio'),
  (u'video', u'video'),
  (u'map', u'map'),
  (u'table', u'table'),
  (u'quotation', u'quotation'),
  (u'text', u'text'),
)

ASSET_STATUS = (
    (u'draft', u'draft'),
    (u'published', u'published'),
)

DEFAULT_STATUS = u'published'

class Asset(TranslatedModel):
    asset_id = UUIDField(auto=True)
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    attribution = models.TextField(blank=True)
    license = models.CharField(max_length=25, choices=LICENSES,
                               default=DEFAULT_LICENSE)
    status = models.CharField(max_length=10, choices=ASSET_STATUS, default=DEFAULT_STATUS)
    owner = models.ForeignKey(User, related_name="assets", blank=True,
                              null=True)
    section_specific = models.BooleanField(default=False)
    # asset_created is when the asset itself was created
    # e.g. date a photo was taken
    asset_created = models.DateTimeField(blank=True, null=True)
    # created is when the object was created in the system
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(blank=True, null=True)

    translated_fields = ['title', 'caption']

    # Use InheritanceManager from django-model-utils to make
    # fetching of subclassed objects easier
    objects = InheritanceManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('asset_detail', [str(self.asset_id)])

    def license_name(self):
        """ Convert the license code to a more human-readable version """
        return get_license_name(self.license)

    def render(self, format='html'):
        try:
            return getattr(self, "render_" + format).__call__()
        except AttributeError:
            return self.__unicode__()

@receiver(pre_save, sender=Asset)
def set_date_on_published(sender, instance, **kwargs):
    """ Set the published date of a story when it's status is changed to 'published' """
    try:
        asset = Asset.objects.get(pk=instance.pk)
    except Asset.DoesNotExist:
        # Object is new
        if instance.status == 'published':
            instance.published = datetime.now()
    else:
        if instance.status == 'published' and asset.status != 'published':
            instance.published = datetime.now()

class AssetTranslation(TranslationModel):
    asset = models.ForeignKey('Asset', related_name="%(app_label)s_%(class)s_related") 
    title = ShortTextField() 
    caption = models.TextField(blank=True)

    class Meta:
        abstract = True
        unique_together = (('asset', 'language')) 

class ExternalAsset(Asset):
#    translations = models.ManyToManyField('ExternalAssetTranslation', blank=True, verbose_name=_('translations'))

    translation_set = 'storybase_asset_externalassettranslation_related'
    translated_fields = Asset.translated_fields + ['url']

    def render_html(self):
        output = []
        output.append('<figure>')
        try:
            resource = oembed.site.embed(self.url, format='json')
            resource_data = resource.get_data()
            output.append(resource_data['html'])
        except OEmbedMissingEndpoint, e:
            print e
            if self.type == 'image':
                output.append('<img src="%s" alt="%s" />' % (self.url, self.title))
            else:
                output.append("<a href=\"%s\">%s</a>" % (self.url, self.title))

        if self.caption:
            output.append('<figcaption>')
            output.append(self.caption)
            output.append('</figcaption>')
        output.append('</figure>')

        return mark_safe(u'\n'.join(output))

class ExternalAssetTranslation(AssetTranslation):
    url = models.URLField()

class HtmlAsset(Asset):
#    translations = models.ManyToManyField('HtmlAssetTranslation', blank=True, verbose_name=_('translations'))

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

class LocalImageAsset(Asset):
#    translations = models.ManyToManyField('LocalImageAssetTranslation', blank=True, verbose_name=_('translations'))

    translation_set = 'storybase_asset_localimageassettranslation_related'
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

class LocalImageAssetTranslation(AssetTranslation):
    image = FilerImageField()
