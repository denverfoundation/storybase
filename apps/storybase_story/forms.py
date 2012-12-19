"""Custom forms and form fields"""

from django import forms
from django.utils import translation

from tinymce.widgets import TinyMCE

from storybase.widgets import AdminLongTextInputWidget
from storybase_story.fields import SectionModelChoiceField
from storybase_story.models import (Section, SectionRelation,
		                    SectionTranslation, 
		                    Story, StoryTranslation)

class InlineSectionAdminForm(forms.ModelForm):
    """Add an extra field for translation"""
    title = forms.CharField(widget=AdminLongTextInputWidget)

    readonly_fields = ['edit_link',]

    class Meta:
        model = Section
        fields = ('title', 'root', 'layout', 'weight')

    def __init__(self, *args, **kwargs):
        super(InlineSectionAdminForm, self).__init__(*args, **kwargs)

        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            language_code = translation.get_language()
            try:
                instance_trans = instance.sectiontranslation_set.get(
                    language=language_code)

                self.initial['title'] = instance_trans.title
            except SectionTranslation.DoesNotExist:
                pass

    def save(self, commit=True):
        model = super(InlineSectionAdminForm, self).save(commit=False)

        try:
            language_code = translation.get_language()
            trans = model.sectiontranslation_set.get(
                language=language_code)
            if trans.title != self.cleaned_data['title']:
                trans.title = self.cleaned_data['title']
        except SectionTranslation.DoesNotExist:
            # This violates the commit argument, but you can't
            # create the translation without first saving the model.
            model.save()
            trans = SectionTranslation(section=model,
                                       title=self.cleaned_data['title'],
                                       language=language_code)
        finally:
            trans.save()

        if commit:
            model.save()

        return model


class SectionRelationAdminForm(forms.ModelForm):
    """"Custom model form for SectionRelations

    Uses a ModelChoiceField that shows both the section and story title
    to differentiate between sections with the same name.

    """
    parent = SectionModelChoiceField(queryset=Section.objects.all()) 
    child = SectionModelChoiceField(queryset=Section.objects.all())

    class Meta:
	model = SectionRelation


class StoryAdminForm(forms.ModelForm):
    class Meta:
        model = Story 
        widgets = {
            'call_to_action': TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs={
                    'theme': 'advanced',
                    'force_p_newlines': False,
                    'forced_root_block': '',
                    'theme_advanced_toolbar_location': 'top',
                    'plugins': 'table',
                    'theme_advanced_buttons3_add': 'tablecontrols'},
                )
        }

class StoryTranslationAdminForm(forms.ModelForm):
    class Meta:
        model = StoryTranslation 
        widgets = {
            'call_to_action': TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top', 'plugins': 'table', 'theme_advanced_buttons3_add': 'tablecontrols'},
            )
        }
