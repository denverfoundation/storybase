from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from uuidfield.fields import UUIDField

from storybase.fields import ShortTextField
from storybase.models.translation import TranslatedModel, TranslationModel

class HelpTranslation(TranslationModel):
    help = models.ForeignKey('Help')
    title = ShortTextField(blank=True) 
    body = models.TextField(blank=True)
    
    class Meta:
        app_label = 'storybase'


class Help(TranslatedModel):
    help_id = UUIDField(auto=True)
    slug = models.SlugField(blank=True)

    translated_fields = ['body', 'title']
    translation_set = 'helptranslation_set'
    translation_class = HelpTranslation

    class Meta:
        app_label = 'storybase'
        verbose_name_plural = "help items"

    def __unicode__(self):
        if self.title:
            return self.title

        return _("Help Item") + " " + self.help_id


def create_help(title='', body='', language=settings.LANGUAGE_CODE, 
                 *args, **kwargs):
    """Convenience function for creating Help 

    Allows for the creation of help items without having to explicitly
    deal with the translations.

    """
    obj = Help(*args, **kwargs)
    obj.save()
    translation = HelpTranslation(help=obj, title=title, body=body,
                                   language=language)
    translation.save()
    return obj
