"""Models for story content assets"""
import os

import lxml.html

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from filer.fields.image import FilerFileField, FilerImageField
from filer.models import Image 
from micawber.exceptions import ProviderException, ProviderNotFoundException
from model_utils.managers import InheritanceManager
from uuidfield.fields import UUIDField

from storybase.fields import ShortTextField
from storybase.models import (LicensedModel, PublishedModel,
    TimestampedModel, TranslatedModel, TranslationModel,
    PermissionMixin, set_date_on_published)
from storybase.utils import full_url, key_from_instance
from storybase_asset.oembed import bootstrap_providers
from storybase_asset.utils import img_el

ASSET_TYPES = (
  (u'image', u'image'),
  (u'audio', u'audio'),
  (u'video', u'video'),
  (u'map', u'map'),
  (u'chart', u'chart'),
  (u'table', u'table'),
  (u'quotation', u'quotation'),
  (u'text', u'text'),
)
"""The available types of assets

These represent what an asset is and not neccessarily how it is stored.
For example, a map might actually be stored as an image, or it could be
an HTML snippet.
"""

CAPTION_TYPES = ('chart', 'image', 'map', 'table')
"""Assets that display a caption"""


class ImageRenderingMixin(object):
    """
    Mixin for rendering images in Asset-like objects
    """
    def get_img_url(self):
        raise NotImplemented

    def render_img_html(self, url=None, attrs={}):
        """Render an image tag for this asset""" 
        if url is None:
            url = self.get_img_url()
        el_attrs = dict(src=url, alt=self.title)
        el_attrs.update(attrs)
        return mark_safe(img_el(el_attrs))

    def render_thumbnail(self, width=0, height=0, format='html',
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

    def get_thumbnail_url(self, width=0, height=0, **kwargs):
        """Return the URL of the Asset's thumbnail"""
        return None

    def render_thumbnail_html(self, width=0, height=0, **kwargs):
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
            output = self.render_img_html(url, {
                'class': "asset-thumbnail " + html_class})
            
        return mark_safe(output)


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

    def strings(self):
        return None


class Asset(ImageRenderingMixin, TranslatedModel, LicensedModel, 
    PublishedModel, TimestampedModel, AssetPermission):
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
    asset_id = UUIDField(auto=True, db_index=True)
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

    def render(self, format='html', **kwargs):
        """Render a viewable representation of an asset

        Arguments:
        format -- the format to render the asset. defaults to 'html' which
                  is presently the only available option.

        """
        try:
            return getattr(self, "render_" + format).__call__(**kwargs)
        except AttributeError:
            return self.__unicode__()

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

    def strings(self):
        """Print all the strings in all languages for this asset
        
        This is meant to be used to help generate a document for full-text
        search using Haystack.

        """
        strings = []
        translations = getattr(self, self.translation_set)
        for translation in translations.all():
            trans_strings = translation.strings()
            if trans_strings:
                strings.append(trans_strings)

        return " ".join(strings)


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
        maxlength = 100
        if self.title:
            return self.title
        elif self.url:
            url = self.url 
            if len(url) > maxlength:
                url = url[0:maxlength] 
            return url
        else:
            return "Asset %s" % self.asset_id

    def get_img_url(self):
        return self.url

    def render_link_html(self):
        """Render a link for this asset"""
        return "<a href=\"%s\">%s</a>" % (self.url, self.title)

    def render_html(self, **kwargs):
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
                
        except ProviderNotFoundException:
            # URL not matched, just show an image or a link
            if self.type == 'image':
                output.append(self.render_img_html())
            else:
                output.append(self.render_link_html())
        except ProviderException:
            # Some other error occurred with the oEmbed
            # TODO: Show a default image
            output.append(self.render_link_html())
        except ValueError:
            # ValueError is raised when JSON of response couldn't
            # be decoded, e.g. when offline
            # Some other error occurred with the oEmbed
            # TODO: Show a default image
            output.append(self.render_link_html())

        full_caption_html = self.full_caption_html()
        if full_caption_html:
	    output.append(full_caption_html)
        output.append('</figure>')

        return mark_safe(u'\n'.join(output))

    def get_thumbnail_url(self, width=0, height=0, **kwargs):
        """Return the URL of the Asset's thumbnail"""
        url = None
        try:
            # See if we cached the thumbnail url
            url = getattr(self, '_thumbnail_url')
        except AttributeError:
            try:
                # First try to embed the resource via oEmbed
                params = {}
                if self.type == 'image':
                    # We're going to try to get the image as close to
                    # the actual size that we asked for
                    if width >= height:
                        params['maxwidth'] = width
                    else:
                        params['maxheight'] = height
                resource_data = self.get_oembed_response(self.url, **params)
                if resource_data['type'] == 'photo':
                    self._thumbnail_url = resource_data.get('url')
                else:
                    self._thumbnail_url = resource_data.get('thumbnail_url')
            except ProviderNotFoundException:
                if self.type == 'image':
                    # There isn't an oEmbed provider for the URL. Just use the
                    # raw image URL.
                    self._thumbnail_url = self.url
                else:
                    self._thumbnail_url = None
            except ProviderException:
                # Do nothing, return value gets set in finally clause
                pass 
            except ValueError:
                # Do nothing, return value gets set in finally clause
                pass 
            finally:
                url = getattr(self, '_thumbnail_url', None)

        return url


class HtmlAssetTranslation(AssetTranslation):
    """Translatable fields for an HtmlAsset model instance"""
    body = models.TextField(blank=True)

    def strings(self):
        return strip_tags(self.body)

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

    def get_thumbnail_url(self, width=0, height=0, **kwargs):
        """Return the URL of the Asset's thumbnail
        
        This doesn't really make sense for an HTML Asset, but
        there were a number of HTML Assets of type image that
        were created where the HTML contained just an image tag.

        This is a workaround for those cases.  New assets of this
        type won't ever be created because the builder doesn't allow it.
        """
        fragment = lxml.html.fromstring(self.body)
        matching = fragment.cssselect("img")
        if not len(matching):
            return None

        img = matching[0]
        src = img.get('src')
        return src

    def render_html(self, **kwargs):
        """Render the asset as HTML"""

        # sandbox content that has script tags
        body = self.body
        if self.has_script():
            body = '<iframe class="sandboxed-asset" src="%s"></iframe>' % reverse('asset_content_view', kwargs={ "asset_id": self.asset_id })

        output = []
        if self.title:
            output.append('<h3>%s</h3>' % (self.title))
        if self.type in CAPTION_TYPES:
            output.append('<figure>')
            output.append(body)
            full_caption_html = self.full_caption_html()
            if full_caption_html:
                output.append(full_caption_html)
            output.append('</figure>')
        elif self.type == 'quotation':
            output.append('<blockquote class="quotation">')
            output.append(body)
            if self.attribution:
                attribution = self.attribution
                if self.source_url:
                    attribution = ('<a href="%s">%s</a>' %
                                   (self.source_url, attribution))
                output.append('<p class="attribution">%s</p>' %
                              (attribution))
            output.append('</blockquote>')
        else:
            output.append(body)
            
        return mark_safe(u'\n'.join(output))

    def has_script(self, **kwargs):
        """Return True if the asset has a script tag anywhere within it"""
        return "<script" in self.body.lower()

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

    def get_img_url(self):
        return self.image.url

    def render_html(self, **kwargs):
        """Render the asset as HTML"""
        output = []
        output.append('<figure>')
        output.append(self.render_img_html(**kwargs))
        full_caption_html = self.full_caption_html()
        if full_caption_html:
            output.append(full_caption_html)
        output.append('</figure>')
            
        return mark_safe(u'\n'.join(output))

    def get_thumbnail_url(self, width=0, height=0, **kwargs):
        """Return the URL of the Asset's thumbnail"""
        include_host = kwargs.get('include_host', False)
        if not self.image:
            return None
        thumbnailer = self.image.easy_thumbnails_thumbnailer
        thumbnail_options = {
            # Disable crop for now in favor of CSS cropping, but this
            # is how you would do it. This particular argument crops
            # from the center on the x-axis and the top edge of the
            # image on the y-axis.  
            # See http://easy-thumbnails.readthedocs.org/en/latest/ref/processors/#easy_thumbnails.processors.scale_and_crop
            #'crop': ',0',
            'size': (width, height),
        }
        thumbnail = thumbnailer.get_thumbnail(thumbnail_options)
        if include_host:
            return full_url(thumbnail.url)
        else:
            return thumbnail.url


# Hook up some signals so the publication date gets changed
# on status changes
pre_save.connect(set_date_on_published, sender=ExternalAsset)
pre_save.connect(set_date_on_published, sender=HtmlAsset)
pre_save.connect(set_date_on_published, sender=LocalImageAsset)


class DefaultImageMixin(object):
    """
    Mixin for models that have some related image that needs a 
    default value to fall back on
    """
    @classmethod
    def get_default_img_url_choices(cls):
        # This should be implemented in the subclass
        raise NotImplemented

    @classmethod
    def get_default_img_url(cls, width, height):
        choices = cls.get_default_img_url_choices()
        lgst_width = 0
        lgst_src = None
        for img_width, url in choices.iteritems():
            if img_width <= width and img_width > lgst_width: 
                lgst_src = url
                lgst_width = img_width
        return lgst_src

    @classmethod
    def render_default_img_html(cls, width=500, height=0, attrs={}):
        url = cls.get_default_img_url(width, height)
        el_attrs = dict(src=url)
        el_attrs.update(attrs)
        return mark_safe(img_el(el_attrs))


class FeaturedAssetsMixin(DefaultImageMixin):
    """
    Mixins for models that have a featured asset
    
    Models mixing in this class should have a ManyToMany field
    named ``featured_assets``.  This field is not defined in this mixin mostly
    because I couldn't think of a clever way to set the reverse name the way
    I wanted.
    """
    def get_featured_asset(self):
        """Return the featured asset"""
        if self.featured_assets.count():
            # Return the first featured asset.  We have the ability of 
            # selecting multiple featured assets.  Perhaps in the future
            # allow for specifying a particular feature asset or randomly
            # displaying one.
            return self.featured_assets.select_subclasses()[0]

        return None

    def render_featured_asset(self, format='html', width=500, height=0):
        """Render a representation of the story's featured asset"""
        featured_asset = self.get_featured_asset()
        if featured_asset is None:
            # No featured assets
            return self.render_default_img_html(width, height)
        else:
            # TODO: Pick default size for image
            # Note that these dimensions are the size that the resized
            # image will fit in, not the actual dimensions of the image
            # that will be generated
            # See http://easy-thumbnails.readthedocs.org/en/latest/usage/#thumbnail-options
            thumbnail_options = {
                'width': width,
                'height': height
            }
            if format == 'html':
                thumbnail_options.update({'html_class': 'featured-asset'})
            return featured_asset.render_thumbnail(format=format, 
                                                   **thumbnail_options)

    def featured_asset_thumbnail_url_key(self, include_host=True):
        extra = "fa_url"
        if include_host:
            extra = extra + "_host"
        return key_from_instance(self, extra)

    def featured_asset_thumbnail_url(self, include_host=True):
        """Return the URL of the featured asset's thumbnail

        Returns None if the asset cannot be converted to a thumbnail image.

        """
        key = self.featured_asset_thumbnail_url_key(include_host)
        url = cache.get(key)
        if url:
            return url

        # Cache miss
        featured_asset = self.get_featured_asset()
        if featured_asset is None:
            # No featured assets
            url = self.get_default_img_url(width=222, height=222)
        else:
            thumbnail_options = {
                'width': 240,
                'height': 240,
                'include_host': include_host
            }
            url = featured_asset.get_thumbnail_url(**thumbnail_options)
        cache.set(key, url)
        return url


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
    dataset_id = UUIDField(auto=True, db_index=True)
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


