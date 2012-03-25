from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils import translation
from uuidfield.fields import UUIDField

LICENSES = (
   ('CC BY-NC-SA', u'Attribution-NonCommercial-ShareAlike Creative Commons'),
   ('CC BY-NC', u'Attribution-NonCommercial Creative Commons'),
   ('CC BY-NC-ND', u'Attribution-NonCommercial-NoDerivs Creative Commons'),
   ('CC BY', u'Attribution Creative Commons'),
   ('CC BY-SA', u'Attribution-ShareAlike Creative Commons'),
   ('CC BY-ND', u'Attribution-NoDerivs Creative Commons'),
   ('none', u'None (All rights reserved)')
)

DEFAULT_LICENSE = 'CC BY-NC-SA'

STATUS = (
    (u'draft', u'draft'),
    (u'published', u'published'),
)

DEFAULT_STATUS = u'draft'

def get_license_name(license_code):
    licenses = dict(LICENSES)
    return licenses[license_code]

class TranslatedModel(models.Model):
    translated_fields = []
    _translation_cache = None

    def __init__(self, *args, **kwargs):
        super(TranslatedModel, self).__init__(*args, **kwargs)
        self._translation_cache = {}

    def __getattribute__(self, name):
        """ Attribute getter that searches for fields on the translation model class

        This implementation is based on the one in django-mothertongue by 
        Rob Charlwood https://github.com/robcharlwood/django-mothertongue
        """
        get = lambda p:super(TranslatedModel, self).__getattribute__(p)
        translated_fields = get('translated_fields') 
        if name in translated_fields:
            try:
                translation_set = get('translation_set')
            except AttributeError:
                # Try the subclass
                subclass_attrs = [rel.var_name for rel in self._meta.get_all_related_objects()
                                  if isinstance(rel.field, OneToOneField)
                                  and issubclass(rel.field.model, self.__class__)]
                for attr in subclass_attrs:
                    if hasattr(self, attr):
                        subclass = get(attr)
                        if subclass:
                            translation_set = subclass.translation_set
                            break
                else:
                    raise

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
                    try:
                        translated_object = translated_manager.get(language=new_code)
                    except ObjectDoesNotExist:
                        # If a translation doesn't exist in the 
                        # current language, try the default language
                        try:
                            translated_object = translated_manager.get(language=settings.LANGUAGE_CODE)
                        except ObjectDoesNotExist:
                            # If all else fails, get the first
                            # translation we know about
                            translated_object = translated_manager.all()[0]

            finally:
                self._translation_cache[code] = translated_object
            if translated_object:
                return getattr(translated_object, name)

        return get(name)

    def get_languages(self):
        translation_set = getattr(self, 'translation_set')
        translated_manager = getattr(self, translation_set)
        return [translation.language for translation in translated_manager.all()]

    class Meta:
        abstract = True

class TranslationModel(models.Model):
    translation_id = UUIDField(auto=True)
    language = models.CharField(max_length=15, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    class Meta:
        abstract = True

class TimestampedModel(models.Model):
    """ Abstract base class that provides created and last edited fields """
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class PublishedModel(models.Model):
    """ Abstract base class that provides a status field and a publication date """
    status = models.CharField(max_length=10, choices=STATUS, default=DEFAULT_STATUS)
    published = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

class LicensedModel(models.Model):
    """ Abstract base class that provides a field representing the instance's licensing status """
    license = models.CharField(max_length=25, choices=LICENSES,
                               default=DEFAULT_LICENSE)

    class Meta:
        abstract = True

    def license_name(self):
        """ Convert the license code to a more human-readable version """
        return get_license_name(self.license)

# Signal handlers

def set_date_on_published(sender, instance, **kwargs):
    """  Set the published date of a story when it's status is changed to 'published' 
    
    For models inheriting from PublishedModel

    """
   
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Object is new, so field won't have changed.
        # Just check status.
        if instance.status == 'published':
            instance.published = datetime.now()
    else:
        if instance.status == 'published' and old_instance.status != 'published':
            instance.published = datetime.now()
