from django import forms
from tinymce.widgets import TinyMCE
from cmsplugin_storybase.models import NewsItemTranslation

class NewsItemTranslationAdminForm(forms.ModelForm):
    class Meta:
        model = NewsItemTranslation 
        widgets = {
            'body': TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top', 'plugins': 'table', 'theme_advanced_buttons3_add': 'tablecontrols'},
            )
        }
