from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils import translation

from uuidfield.fields import UUIDField

from storybase.utils import get_language_name

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

    def clear_translation_cache(self):
        self._translation_cache = {}

    def set_translation_cache_item(self, code, obj):
        self._translation_cache[code] = obj

    def get_languages(self):
        """Get a list of translated languages for the model instance"""
        # TODO: Refactor this so it doesn't repeat the code in 
        # __getattribute__
        try:
            translation_set = getattr(self, 'translation_set')
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
                    subclass = getattr(self, attr)
                    if subclass:
                        translation_set = subclass.translation_set
                        break
            else:
                raise
        translated_manager = getattr(self, translation_set)
        return [trans.language 
                for trans in translated_manager.all()]

    def get_language_urls(self):
        """Return a list of language codes, full names and URLs"""
        return [{ 'id': code, 'name': get_language_name(code), 'url': "/%s%s" % (code, self.get_absolute_url()) }
                for code in self.get_languages()]

    def get_language_names(self):
        """Return a list of language_codes and full names"""
        return [{ 'id': code, 'name': get_language_name(code) }
                for code in self.get_languages()]

    def get_language_info(self):
        if hasattr(self, 'get_absolute_url'):
            return self.get_language_urls()
        else:
            return self.get_language_names()

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
