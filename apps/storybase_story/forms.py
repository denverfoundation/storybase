"""Custom forms and form fields"""

#import calendar
#from datetime import datetime, date
from itertools import chain

from django import forms
from django.utils import translation
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

#from haystack.forms import FacetedSearchForm
from tinymce.widgets import TinyMCE

from storybase.widgets import AdminLongTextInputWidget
from storybase_story.fields import SectionModelChoiceField
from storybase_story.models import (Section, SectionRelation,
		                    SectionTranslation, 
		                    Story, StoryTranslation)


class GroupedCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, attrs=None, choices=(), choice_groups=()):
        super(GroupedCheckboxSelectMultiple, self).__init__(attrs)
        self.choice_groups = list(choice_groups)

    def render(self, name, value, attrs=None, choices=(), choice_groups=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        str_values = set([force_unicode(v) for v in value])
        i = 0
        for choice_group in chain(self.choice_groups, choice_groups):
            output.append(u'<li>')
            output.append(choice_group['label'])
            output.append(u'<ul>')
            for (option_value, option_label) in choice_group['choices']:
                # If an ID attribute was given, add a numeric index as a suffix,
                # so that the checkboxes don't all have the same ID attribute.
                if has_id:
                    final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                    label_for = u' for="%s"' % final_attrs['id']
                else:
                    label_for = ''

                cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
                option_value = force_unicode(option_value)
                rendered_cb = cb.render(name, option_value)
                option_label = conditional_escape(force_unicode(option_label))
                output.append(u'<li><label%s>%s %s</label></li>' % (label_for, rendered_cb, option_label))
                i += 1
            output.append(u'</ul>')
            output.append(u'</li>')

        return mark_safe(u'\n'.join(output))


class GroupedMultipleChoiceField(forms.MultipleChoiceField):
    widget = GroupedCheckboxSelectMultiple

    def __init__(self, choice_groups=(), *args, **kwargs):
        def _flatten_choices(choice_groups):
            return [choice for group in choice_groups 
                    for choice in group['choices']]
                    
        super(GroupedMultipleChoiceField, self).__init__(
            choices=_flatten_choices(choice_groups), *args, **kwargs)
        self.choice_groups = choice_groups

    def _get_choice_groups(self):
        return self._choice_groups

    def _set_choice_groups(self, value):
        self._choice_groups = self.widget.choice_groups = list(value)

    choice_groups = property(_get_choice_groups, _set_choice_groups)

#class StoryFacetedSearchForm(FacetedSearchForm):
#    @classmethod
#    def parse_date(cls, datestr):
#        return datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ').date()
#
#    @classmethod
#    def format_mo_yr(cls, datestr):
#        return cls.parse_date(datestr).strftime('%B, %Y')
#        
#    def __init__(self, *args, **kwargs):
#        super(StoryFacetedSearchForm, self).__init__(*args, **kwargs)
#        facet_fields = kwargs['searchqueryset'].facet_counts()['fields']
#        choice_groups = []
#        for name, tags in facet_fields.items():
#            if len(tags):
#                choice_group = dict(label=name.capitalize(), choices=[])
#                for tag in tags:
#                    choice_group['choices'].append(("%s:%s" % (name, tag[0]), "%s (%d)" % (tag[0], tag[1])))
#                choice_groups.append(choice_group)
#
#        pub_date_field = kwargs['searchqueryset'].facet_counts()['dates']['pub_date']
#        choice_group = dict(label='Publication Date', choices=[])
#        for facet_date, count in pub_date_field.items():
#            if count > 0 and facet_date not in ('start', 'end', 'gap'):
#                choice_group['choices'].append(("pub_date:%s" % (facet_date), "%s (%d)" % (self.__class__.format_mo_yr(facet_date), count)))
#        choice_groups.append(choice_group)
#
#        self.fields['selected_facets'] = GroupedMultipleChoiceField(choice_groups=choice_groups, required=False, label='Facets')
#
#    def no_query_found(self):
#        return self.searchqueryset.all()
#
#    def search(self):
#        sqs = super(FacetedSearchForm, self).search()
#        
#        # We need to process each facet to ensure that the field name and the
#        # value are quoted correctly and separately:
#        for facet in self.selected_facets:
#            if ":" not in facet:
#                continue
#            
#            field, value = facet.split(":", 1)
#           
#            if field == 'pub_date' and value:
#                # If the facet is for a date, filter instead of narrowing
#                date_value = self.__class__.parse_date(value)
#                first_date_of_month = date_value
#                last_day_of_month = calendar.monthrange(first_date_of_month.year, first_date_of_month.month)[1]
#                last_date_of_month = date(first_date_of_month.year, first_date_of_month.month, last_day_of_month)
#                sqs = sqs.filter(pub_date__gte=first_date_of_month, pub_date__lte=last_date_of_month)
#
#            elif value:
#                sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))
#        
#        return sqs


class InlineSectionAdminForm(forms.ModelForm):
    """Add an extra field for translation"""
    title = forms.CharField(widget=AdminLongTextInputWidget)

    readonly_fields = ['edit_link',]

    class Meta:
        model = Section
        fields = ('title', 'root', 'weight')

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
