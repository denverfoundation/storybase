"""Custom forms and form fields"""

from django import forms
from django.utils import translation

from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet

from tinymce.widgets import TinyMCE

from storybase_geo.models import Place
from storybase_taxonomy.models import Category
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
        # TODO: explicitly list fields
        fields = '__all__'


class StoryAdminForm(forms.ModelForm):
    class Meta:
        model = Story 
        # TODO: explicitly list fields
        fields = '__all__'
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
        # TODO: explicitly list fields
        fields = '__all__'
        widgets = {
            'call_to_action': TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top', 'plugins': 'table', 'theme_advanced_buttons3_add': 'tablecontrols'},
            )
        }


class StorySearchForm(SearchForm):
    """
    A custom search that allows user to optionally search based on a
    single topic and/or place ID.

    """
    topic = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    place = forms.ModelChoiceField(queryset=Place.objects.all(), required=False)

    def search(self):
        sqs = super(StorySearchForm, self).search()

        if isinstance(sqs, EmptySearchQuerySet):
            return sqs

        topic = self.cleaned_data.get('topic', None)

        if topic is not None:
            sqs = sqs.filter(topic_ids__in=[topic.id])

        place = self.cleaned_data.get('place', None)

        if place is not None:
            sqs = sqs.filter(place_ids__in=[place.id])

        return sqs
