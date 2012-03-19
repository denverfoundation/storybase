from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import translation
from uuidfield.fields import UUIDField

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
            except (ObjectDoesNotExist, AttributeError):
                # If title attribute doesn't exist on the Asset model, 
                # try the subclass.
                if name == 'title':
                    return getattr(self.subclass(), name)

        return get(name)

    class Meta:
        abstract = True

class TranslationModel(models.Model):
    translation_id = UUIDField(auto=True)
    language = models.CharField(max_length=15, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    class Meta:
        abstract = True
