from django.db import models

from uuidfield.fields import UUIDField

from storybase.models.translation import TranslatedModel, TranslationModel

class HelpTranslation(TranslationModel):
    help = models.ForeignKey('Help')
    body = models.TextField(blank=True)
    
    class Meta:
        app_label = 'storybase'


class Help(TranslatedModel):
    help_id = UUIDField(auto=True)
    slug = models.SlugField(blank=True)

    translated_fields = ['body']
    translation_set = 'helptranslation_set'
    translation_class = HelpTranslation

    class Meta:
        app_label = 'storybase'

