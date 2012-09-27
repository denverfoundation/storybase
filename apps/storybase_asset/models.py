"""Models for story content assets"""
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files import File
from django.db import models
from django.db.models.signals import pre_save, pre_delete, post_delete
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from filer.fields.image import FilerFileField, FilerImageField
from filer.models import Image 
from micawber.exceptions import ProviderException
from model_utils.managers import InheritanceManager
from uuidfield.fields import UUIDField

from storybase.fields import ShortTextField
from storybase.models import (LicensedModel, PublishedModel,
    TimestampedModel, TranslatedModel, TranslationModel,
    PermissionMixin, set_date_on_published)
from storybase_asset.oembed import bootstrap_providers

ASSET_TYPES = (
  (u'image', u'image'),
  (u'audio', u'audio'),
  (u'video', u'video'),
  (u'map', u'map'),
  (u'table', u'table'),
  (u'quotation', u'quotation'),
  (u'text', u'text'),
)
"""The available types of assets

These represent what an asset is and not neccessarily how it is stored.
For example, a map might actually be stored as an image, or it could be
an HTML snippet.
"""

class AssetPermission(PermissionMixin):
    """Permissions for the Asset model"""
    def user_can_change(self, user):
        from storybase_user.utils import is_admin

        if not user.is_active:
            return False

        # Authenticated, active users can change their own assets
        if self.owner == user:
            return True

        # Admins can change any asset
        if is_admin(user):
            return True

        return False

    def user_can_add(self, user):
        # All authenticated, active users can add assets
        if not user.is_active:
            return False

        return True

    def user_can_delete(self, user):
        return self.user_can_change(user)

class AssetTranslation(TranslationModel):
    """
    Abstract base class for common translated metadata fields for Asset
    instances
    """
    asset = models.ForeignKey('Asset',  
        related_name="%(app_label)s_%(class)s_related") 
    title = ShortTextField(blank=True) 
    caption = models.TextField(blank=True)

    class Meta:
        abstract = True
        unique_together = (('asset', 'language')) 

class Asset(TranslatedModel, LicensedModel, PublishedModel,
    TimestampedModel, AssetPermission):
    """A piece of content included in a story

    An asset could be an image, a block of text, an embedded resource
    represented by an HTML snippet or a media file.
    
    This is a base class that provides common metadata for the asset.
    However, it does not provide the fields that specify the content
    itself.  Also, to reduce the number of database tables and queries
    this model class does not provide translated metadata fields.  When
    creating an asset, one shouldn't instantiate this class, but instead
    use one of the model classes that inherits form Asset.

    """
    asset_id = UUIDField(auto=True)
    type = models.CharField(max_length=10, choices=ASSET_TYPES)
    attribution = models.TextField(blank=True)
    source_url = models.URLField(blank=True)
    """The URL where an asset originated.

    It could be used to store the canonical URL for a resource that is not
    yet oEmbedable or the canonical URL of an article or tweet where text 
    is quoted from.

    """
    owner = models.ForeignKey(User, related_name="assets", blank=True,
                              null=True)
    section_specific = models.BooleanField(default=False)
    datasets = models.ManyToManyField('DataSet', related_name='assets', 
                                      blank=True)
    asset_created = models.DateTimeField(blank=True, null=True)
    """Date/time the non-digital version of an asset was created

    For example, the data a photo was taken
    """

    translated_fields = ['title', 'caption']
    translation_class = AssetTranslation

    # Use InheritanceManager from django-model-utils to make
    # fetching of subclassed objects easier
    objects = InheritanceManager()

    def __unicode__(self):
        subclass_obj = Asset.objects.get_subclass(pk=self.pk)
        return subclass_obj.__unicode__()

    @models.permalink
    def get_absolute_url(self):
        return ('asset_detail', [str(self.asset_id)])

    def display_title(self):
        """
        Wrapper to handle displaying some kind of title when the
        the title field is blank 
        """
        # For now just call the __unicode__() method
        return unicode(self)

    def render(self, format='html'):
        """Render a viewable representation of an asset

        Arguments:
        format -- the format to render the asset. defaults to 'html' which
                  is presently the only available option.

        """
        try:
            return getattr(self, "render_" + format).__call__()
        except AttributeError:
            return self.__unicode__()

    def render_thumbnail(self, width=150, height=100, format='html',
                         **kwargs):
        """Render a thumbnail-sized viewable representation of an asset 

        Arguments:
        height -- Height of the thumbnail in pixels
        width  -- Width of the thumbnail in pixels
        format -- the format to render the asset. defaults to 'html' which
                  is presently the only available option.

        """
        return getattr(self, "render_thumbnail_" + format).__call__(
            width, height, **kwargs)

    def render_thumbnail_html(self, width=150, height=100, **kwargs):
        """
        Render HTML for a thumbnail-sized viewable representation of an 
        asset 

        This just provides a dummy placeholder and should be implemented
        classes that inherit from Asset.

        Arguments:
        height -- Height of the thumbnail in pixels
        width  -- Width of the thumbnail in pixels

        """
        html_class = kwargs.get('html_class', "")
        return mark_safe("<div class='asset-thumbnail %s' "
                "style='height: %dpx; width: %dpx'>Asset Thumbnail</div>" %
                (html_class, height, width))

    def get_thumbnail_url(self, width=150, height=100, **kwargs):
        """Return the URL of the Asset's thumbnail"""
        return None

    def dataset_html(self, label=_("Associated Datasets")):
        """Return an HTML list of associated datasets"""
        output = []
        if self.datasets.count():
            download_label = _("Download the data")
            output.append("<p class=\"datasets-label\">%s:</p>" %
                          label)
            output.append("<ul class=\"datasets\">")
            for dataset in self.datasets.select_subclasses():
                download_label = (_("Download the data") 
				  if dataset.links_to_file
				  else _("View the data"))
                output.append("<li>%s <a href=\"%s\">%s</a></li>" % 
                              (dataset.title, dataset.download_url(),
                               download_label))
            output.append("</ul>")
        return mark_safe(u'\n'.join(output))

    def full_caption_html(self, wrapper='figcaption'):
        """Return the caption and attribution text together"""
        output = ""
        if self.caption:
            output += "<div class='caption'>%s</div>" % (self.caption)
        if self.attribution:
            attribution = self.attribution
            if self.source_url:
                attribution = "<a href='%s'>%s</a>" % (self.source_url,
                    attribution)
            output += "<div class='attribution'>%s</div>" % (attribution)

        dataset_html = self.dataset_html()
        if dataset_html:
            output += dataset_html

        if output:
            output = '<%s>%s</%s>' % (wrapper, output, wrapper)

        return output
        

class ExternalAssetTranslation(AssetTranslation):
    """Translatable fields for an Asset model instance"""
    url = models.URLField(max_length=500)


class ExternalAsset(Asset):
    """Asset not stored on the same system as the application

    An ExternalAsset's resource can either be retrieved via an oEmbed API
    endpoint or in the case of an image or other media file, the file's
    URL.
    """
    translation_set = 'storybase_asset_externalassettranslation_related'
    translated_fields = Asset.translated_fields + ['url']
    translation_class = ExternalAssetTranslation

    oembed_providers = bootstrap_providers() 

    @classmethod
    def get_oembed_response(cls, url, **extra_params):
        return cls.oembed_providers.request(url, **extra_params)

    def __unicode__(self):
        if self.title:
            return self.title
        elif self.url:
            return self.url
        else:
            return "Asset %s" % self.asset_id

    def render_img_html(self, url=None):
        """Render an image tag for this asset"""
        assert self.type == 'image'
        if url is None:
            url = self.url
        return "<img src='%s' alt='%s' />" % (url, self.title)

    def render_link_html(self):
        """Render a link for this asset"""
        return "<a href=\"%s\">%s</a>" % (self.url, self.title)

    def render_html(self):
        """Render the asset as HTML"""
        output = []
        output.append('<figure>')
        try:
            # First try to embed the resource via oEmbed
            # TODO: Set maxwidth and maxheight more intelligently
            # Hard-coding them is just a workaround for #130 as the Flickr API
            # doesn't support not having them.
            # TODO: Check if we need to hard-code maxwidth for Flickr
            # e.g. resource_data = self.get_oembed_response(self.url, maxwidth=1000, maxheight=1000)
            resource_data = self.get_oembed_response(self.url)  
            if resource_data['type'] in ('rich', 'video'):
                output.append(resource_data['html'])
            elif resource_data['type'] == 'photo':
                output.append(self.render_img_html(resource_data['url']))
            elif resource_data['type'] == 'link':
                output.append(self.render_link_html())
            else:
                raise AssertionError(
                    "oEmbed provider returned invalid type")
                
        except ProviderException:
            # URL not matched, just show an image or a link
            if self.type == 'image':
                output.append(self.render_img_html())
            else:
                output.append(self.render_link_html())

        full_caption_html = self.full_caption_html()
        if full_caption_html:
	    output.append(full_caption_html)
        output.append('</figure>')

        return mark_safe(u'\n'.join(output))

    def render_thumbnail_html(self, width=150, height=100, **kwargs):
        """
        Render HTML for a thumbnail-sized viewable representation of an 
        asset 

        Arguments:
        height -- Height of the thumbnail in pixels
        width  -- Width of the thumbnail in pixels

        """
        html_class = kwargs.get('html_class', '')
        url = self.get_thumbnail_url(width, height)
        output = ("<div class='asset-thumbnail %s' "
                  "style='height: %dpx; width: %dpx'>"
                  "Asset Thumbnail</div>" % (html_class, height, width))
        if url is not None: 
            output = "<img class='asset-thumbnail %s' src='%s' alt='%s' />" % (html_class, url, self.title)
            
        return mark_safe(output)

    def get_thumbnail_url(self, width=150, height=100, **kwargs):
        """Return the URL of the Asset's thumbnail"""
        url = None
        try:
            # See if we cached the thumbnail url
            url = getattr(self, '_thumbnail_url')
        except AttributeError:
            try:
                # First try to embed the resource via oEmbed
                resource_data = self.get_oembed_response(self.url)
                self._thumbnail_url = resource_data.get('thumbnail_url',
                                                        None)
            except (ProviderException):
                self._thumbnail_url = None
            finally:
                url = self._thumbnail_url

        return url


class HtmlAssetTranslation(AssetTranslation):
    """Translatable fields for an HtmlAsset model instance"""
    body = models.TextField(blank=True)


class HtmlAsset(Asset):
    """An Asset that can be stored as a block of HTML.

    This can store formatted text or an HTML snippet for an embedable
    resource.

    The text stored in an HtmlAsset doesn't have to contain HTML markup.

    """
    translation_set = 'storybase_asset_htmlassettranslation_related'
    translated_fields = Asset.translated_fields + ['body']
    translation_class = HtmlAssetTranslation

    def __unicode__(self):
        """ String representation of asset """
        maxlength = 100
        if self.title:
            return self.title
        elif self.body:
            title = truncate_words(strip_tags(mark_safe(self.body)), 4)
            # Workaround for cases when there's javascript in the body
            # with no spaces
            if len(title) > maxlength:
                title = title[0:maxlength]
            return title
        else:
            return 'Asset %s' % self.asset_id

    def render_html(self):
        """Render the asset as HTML"""
        output = []
        if self.title:
            output.append('<h3>%s</h3>' % (self.title))
        if self.type in ('image', 'map', 'table'):
            output.append('<figure>')
            output.append(self.body)
            full_caption_html = self.full_caption_html()
            if full_caption_html:
                output.append(full_caption_html)
            output.append('</figure>')
        elif self.type == 'quotation':
            output.append('<blockquote>')
            output.append(self.body)
            if self.attribution:
                attribution = self.attribution
                if self.source_url:
                    attribution = ('<a href="%s">%s</a>' %
                                   (self.source_url, attribution))
                output.append('<p class="attribution">%s</p>' %
                              (attribution))
            output.append('</blockquote>')
        else:
            output.append(self.body)
            
        return mark_safe(u'\n'.join(output))


class LocalImageAssetTranslation(AssetTranslation):
    """Translatable fields for a LocalImageAsset model instance"""
    image = FilerImageField(null=True)


class LocalImageAsset(Asset):
    """
    An asset that can be stored as an image file accessible by the
    application through a Django API
    
    This currently uses the `django-filer <https://github.com/stefanfoulis/django-filer>`_ 
    application for storing images as this app adds a lot of convenience
    for working with images in the Django admin.  This is subject to change.
    
    """
    translation_set = 'storybase_asset_localimageassettranslation_related'
    translated_fields = Asset.translated_fields + ['image']
    translation_class = LocalImageAssetTranslation

    def __unicode__(self):
        if self.title:
            return self.title
        elif self.image:
            return os.path.basename(self.image.file.name)
        else:
            return "Asset %s" % self.asset_id

    def render_html(self):
        """Render the asset as HTML"""
        output = []
        output.append('<figure>')
        output.append('<img src="%s" alt="%s" />' % (self.image.url, 
                                                     self.title))
        full_caption_html = self.full_caption_html()
        if full_caption_html:
	    output.append(full_caption_html)
        output.append('</figure>')
            
        return mark_safe(u'\n'.join(output))

    def render_thumbnail_html(self, width=150, height=100, **kwargs):
        """
        Render HTML for a thumbnail-sized viewable representation of an 
        asset 

        Arguments:
        height -- Height of the thumbnail in pixels
        width  -- Width of the thumbnail in pixels

        """
        html_class = kwargs.get('html_class', "")
        thumbnailer = self.image.easy_thumbnails_thumbnailer
        thumbnail_options = {}
        thumbnail_options.update({'size': (width, height)})
        thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
        return mark_safe("<img class='asset-thumbnail %s' "
            "src='%s' alt='%s' />" %
            (html_class, thumbnail.url, self.title))

    def get_thumbnail_url(self, width=150, height=100, **kwargs):
        """Return the URL of the Asset's thumbnail"""
        include_host = kwargs.get('include_host', False)
        if not self.image:
            return None
        thumbnailer = self.image.easy_thumbnails_thumbnailer
        thumbnail_options = {}
        thumbnail_options.update({'size': (width, height)})
        thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
        host = "http://%s" % (Site.objects.get_current().domain) if include_host else ""
        return "%s%s" % (host, thumbnail.url)
                               


# Hook up some signals so the publication date gets changed
# on status changes
pre_save.connect(set_date_on_published, sender=ExternalAsset)
pre_save.connect(set_date_on_published, sender=HtmlAsset)
pre_save.connect(set_date_on_published, sender=LocalImageAsset)


class DataSetPermission(PermissionMixin):
    """Permissions for the DataSet model"""
    def user_can_change(self, user):
        from storybase_user.utils import is_admin

        if not user.is_active:
            return False

        # Authenticated, active users can change their own dataset 
        if self.owner == user:
            return True

        # Admins can change any asset
        if is_admin(user):
            return True

        return False

    def user_can_add(self, user):
        # All authenticated, active users can add assets
        if not user.is_active:
            return False

        return True

    def user_can_delete(self, user):
        return self.user_can_change(user)


class DataSetTranslation(TranslationModel):
    """Translatable fields for a DataSet model instance"""
    dataset = models.ForeignKey('DataSet', 
        related_name="%(app_label)s_%(class)s_related") 
    title = ShortTextField() 
    description = models.TextField(blank=True)

    class Meta:
        unique_together = (('dataset', 'language')) 


class DataSet(TranslatedModel, PublishedModel, TimestampedModel,
    DataSetPermission):
    """
    A set of data related to a story or used to produce a visualization
    included in a story

    This is a base class that provides common metadata for the data set.
    However, it does not provide the fields that specify the content itself.
    When creating a data set, one shouldn't instatniate this class, but
    instead use one of the model classes that inherits from DataSet.

    """
    dataset_id = UUIDField(auto=True)
    source = models.TextField(blank=True)
    attribution = models.TextField(blank=True)
    links_to_file = models.BooleanField(_("Links to file"), default=True)
    """
    Whether the dataset links to a file that can be downloaded or to
    a view of the data or a page describing the data.
    """
    owner = models.ForeignKey(User, related_name="datasets", blank=True,
                              null=True)
    # dataset_created is when the data set itself was created
    dataset_created = models.DateTimeField(blank=True, null=True)
    """
    When the data set itself was created (possibly in non-digital form)
    """

    translation_set = 'storybase_asset_datasettranslation_related'
    translated_fields = ['title', 'description']
    translation_class = DataSetTranslation

    # Use InheritanceManager from django-model-utils to make
    # fetching of subclassed objects easier
    objects = InheritanceManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('dataset_detail', [str(self.dataset_id)])

    @property
    def download_url(self):
        """Returns the URL to the downloadable version of the data set"""
        raise NotImplemented


class ExternalDataSet(DataSet):
    """A data set stored on a different system from the application"""
    url = models.URLField()

    def download_url(self):
        """Returns the URL to the downloadable version of the data set"""
        return self.url 


class LocalDataSet(DataSet):
    """
    A data set stored as a file accessible by the application through
    a Django API

    This currently uses the `django-filer <https://github.com/stefanfoulis/django-filer>`_ 
    application for storing files as this app adds a lot of convenience
    for working with files in the Django admin.  This is subject to change.
    
    """
    file = FilerFileField(null=True)

    def download_url(self):
        """Returns the URL to the downloadable version of the data set"""
        if self.file:
            return self.file.url
        else:
            return None


def delete_dataset_file(sender, instance, **kwargs):
    """
    Delete the filer object and the underlying file when the dataset
    is deleted

    This should be hooked up to the post_delete signal

    """
    if instance.file:
        storage, path = instance.file.file.storage, instance.file.file.path
        instance.file.delete();
        storage.delete(path)

post_delete.connect(delete_dataset_file, sender=LocalDataSet)


def create_html_asset(type, title='', caption='', body='', 
                      language=settings.LANGUAGE_CODE, *args, **kwargs):
    """ Convenience function for creating a HtmlAsset

    Allows for creation of Assets without having to explicitly deal with
    the translations.

    """
    obj = HtmlAsset(
        type=type, 
        *args, **kwargs)
    obj.save()
    translation = HtmlAssetTranslation(
        asset=obj, 
        title=title, 
        caption=caption,
        body=body,
        language=language)
    translation.save()
    return obj

def create_external_asset(type, title='', caption='', url='', 
                          language=settings.LANGUAGE_CODE, *args, **kwargs):
    """ Convenience function for creating a HtmlAsset

    Allows for creation of Assets without having to explicitly deal with
    the translations.

    """
    obj = ExternalAsset(
        type=type, 
        *args, **kwargs)
    obj.save()
    translation = ExternalAssetTranslation(
        asset=obj, 
        title=title, 
        caption=caption,
        url=url,
        language=language)
    translation.save()
    return obj

def create_local_image_asset(type, image, image_filename=None,
                             title='', caption='', url='',
                             language=settings.LANGUAGE_CODE,
                             *args, **kwargs):
        image_file = File(image, name=image_filename)
        image = Image.objects.create(owner=kwargs.get('owner', None),
                                     original_filename=image_filename,
                                     file=image_file)
        obj = LocalImageAsset(type=type, *args, **kwargs)
        obj.save()
        translation = LocalImageAssetTranslation(
            asset=obj,
            title=title,
            caption=caption,
            image=image)
        translation.save()
        return obj


def create_external_dataset(title, url, description='',
                            language=settings.LANGUAGE_CODE,
                            *args, **kwargs):
    """ Convenience function for creating an ExternalDataSet

    Allows for creation of a DataSet without having to explicitly deal with
    the translations.

    """
    obj = ExternalDataSet(
        url=url,
        *args, **kwargs)
    obj.save()
    translation = DataSetTranslation(
        dataset=obj, 
        title=title, 
        description=description,
        language=language)
    translation.save()
    return obj
