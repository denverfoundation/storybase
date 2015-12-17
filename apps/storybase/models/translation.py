import logging
import uuid

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.utils import translation

from storybase.utils import get_language_name

class TranslatedModel(models.Model):
    """Store access translated fields on a related model"""

    translated_fields = []
    """List of field names to be translated"""
    _translation_cache = None

    def __init__(self, *args, **kwargs):
        super(TranslatedModel, self).__init__(*args, **kwargs)
        self._translation_cache = {}

    def _get_translated_manager(self):
        """Get the manager for the translation objects"""
        get = lambda p:super(TranslatedModel, self).__getattribute__(p)
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
                    subclass = get(attr)
                    if subclass:
                        translation_set = subclass.translation_set
                        break
            else:
                raise
        return get(translation_set)

    def __getattribute__(self, name):
        """ Getter that searches for fields on the translation model class

        This implementation is based on the one in django-mothertongue by
        Rob Charlwood https://github.com/robcharlwood/django-mothertongue
        """
        get = lambda p:super(TranslatedModel, self).__getattribute__(p)
        translated_fields = get('translated_fields')
        if name in translated_fields:
            code = translation.get_language()
            translated_manager = self._get_translated_manager()
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
                            try:
			        translated_object = translated_manager.all()[0]
                            except IndexError:
                                # Massive fail. There aren't any translations
                                # for some reason.  This shouldn't happen.
                                # Log an error
                                logger = logging.getLogger('storybase.models.translation')
                                logger.error("No translations found for %s model with pk %s" % (self.__class__.__name__, self.pk))
                                return None

            finally:
                self._translation_cache[code] = translated_object
            if translated_object:
                return getattr(translated_object, name)

        return get(name)

    def clear_translation_cache(self):
        self._translation_cache = {}

    def set_translation_cache_item(self, code, obj):
        self._translation_cache[code] = obj

    # TODO: Use this within the create_* functions in the different
    # applications, e.g. storybase_story.models.create_story
    def create_translation(self, language, **kwargs):
        related_field_name = self.get_translation_fk_field_name()
        trans_kwargs = {'language': language}
        trans_kwargs.update(kwargs)
        trans_kwargs[related_field_name] = self
        return self.translation_class(**trans_kwargs)

    # TODO: Use this in __getattribute__ above
    def get_translation(self, language=None, create=False):
        """
        Get an instance of the translation model in the specified language

        Keyword arguments:
        language -- the language code of the desired language. Defaults to
                    the currently active language.
        create -- create a new model instance if one matching the requested
                  language is not found
        """
        if language is None:
            language = translation.get_language()
        translated_manager = self._get_translated_manager()
        try:
            return translated_manager.get(language=language)
        except ObjectDoesNotExist:
            if create:
                return self.create_translation(language)
            else:
                raise

    @property
    def language(self):
        code = translation.get_language()
        languages = self.get_languages()
        if code in languages:
            # There's a translation for the current active language
            # return the active language
            return code
        elif settings.LANGUAGE_CODE in languages:
            # There's no translation for the current active language
            # but there is one for the default language.  Return
            # the default language
            return settings.LANGUAGE_CODE
        elif languages:
            # There's no translation for the default language either,
            # but there is some translation.  Return the first translation
            return languages[0]
        else:
            return None

    def get_languages(self):
        """Get a list of translated languages for the model instance"""
        translated_manager = self._get_translated_manager()
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
        # TODO: Cache this value after retrieving it the first time
        for field in cls.translation_class._meta.fields:
            if field.rel and field.rel.to == cls:
                return field.name

        return None

    class Meta:
        """Model metadata options"""
        abstract = True


class TranslationModel(models.Model):
    """Base class for model that encapsulates translated fields"""
    translation_id = models.UUIDField(default=uuid.uuid4)
    language = models.CharField(max_length=15, choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)

    class Meta:
        """Model metadata options"""
        abstract = True
