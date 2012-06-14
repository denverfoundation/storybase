"""Abstract base classes for common Model functionality"""

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils import translation

from uuidfield.fields import UUIDField

from storybase.models.dirtyfields import DirtyFieldsMixin

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

def get_license_name(code):
    """Convert a license's code to its full name
    
    Arguments:
    code -- String representing the first element of a tuple in LICENSES.
            This is what is stored in the database for a LicensedModel.

    """
    licenses = dict(LICENSES)
    return licenses[code]

class TranslatedModel(models.Model):
    """Store access translated fields on a related model"""

    translated_fields = []
    """List of field names to be translated"""
    _translation_cache = None

    def __init__(self, *args, **kwargs):
        super(TranslatedModel, self).__init__(*args, **kwargs)
        self._translation_cache = {}

    def __getattribute__(self, name):
        """ Getter that searches for fields on the translation model class

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
                subclass_attrs = [rel.var_name 
                                  for rel 
                                  in self._meta.get_all_related_objects()
                                  if isinstance(rel.field, OneToOneField)
                                  and issubclass(rel.field.model,
                                                 self.__class__)]
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
        """Get a list of translated languages for the model instance"""
        translation_set = getattr(self, 'translation_set')
        translated_manager = getattr(self, translation_set)
        return [trans.language 
                for trans in translated_manager.all()]


    @classmethod
    def get_translation_fk_field_name(cls):
        """
        Get the name of the ForeignKey field on the translation class
        """
        # TODO: Decide if it's better to just follow the convention and 
        # look for a field that matches the lowercase version of the class'
        # name, i.e. cls.__name__.lower()
        for field in cls.translation_class._meta.fields:
            if field.rel and field.rel.to == cls:
                return field.name

        return None 

    class Meta:
        """Model metadata options"""
        abstract = True


class TranslationModel(models.Model):
    """Base class for model that encapsulates translated fields"""
    translation_id = UUIDField(auto=True)
    language = models.CharField(max_length=15, choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)

    class Meta:
        """Model metadata options"""
        abstract = True

class TimestampedModel(models.Model):
    """ Abstract base class that provides created and last edited fields """
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata options"""
        abstract = True

class PublishedModel(models.Model):
    """Abstract base class for models with publication information"""
    status = models.CharField(max_length=10, choices=STATUS,
                              default=DEFAULT_STATUS)
    published = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Model metadata options"""
        abstract = True

class LicensedModel(models.Model):
    """Abstract base class for models with a license"""
    license = models.CharField(max_length=25, choices=LICENSES,
                               default=DEFAULT_LICENSE)

    class Meta:
        """Model metadata options"""
        abstract = True

    def license_name(self):
        """ Convert the license code to a more human-readable version """
        return get_license_name(self.license)

# Signal handlers

def set_date_on_published(sender, instance, **kwargs):
    """Set the published date of a story on status change
    
    For models inheriting from PublishedModel. Should be connected
    to the pre_save signal.

    """
   
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Object is new, so field won't have changed.
        # Just check status.
        if instance.status == 'published':
            instance.published = datetime.now()
    else:
        if (instance.status == 'published' and 
            old_instance.status != 'published'):
            instance.published = datetime.now()
