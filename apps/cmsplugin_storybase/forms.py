from django import forms
from tinymce.widgets import TinyMCE
from cmsplugin_storybase.models import ActivityTranslation, NewsItemTranslation


tinymce_widget = TinyMCE(
    attrs={'cols': 80, 'rows': 30},
    mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top', 'plugins': 'table', 'theme_advanced_buttons3_add': 'tablecontrols'},
)

class ActivityTranslationAdminForm(forms.ModelForm):
    class Meta:
        model = ActivityTranslation
        # TODO: explicitly list fields
        fields = '__all__'
        widgets = {
            'links': tinymce_widget,
        }


class NewsItemTranslationAdminForm(forms.ModelForm):
    class Meta:
        model = NewsItemTranslation
        # TODO: explicitly list fields
        fields = '__all__'
        widgets = {
            'body': tinymce_widget,
        }
