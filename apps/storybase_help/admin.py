from django import forms
from django.conf import settings
from django.contrib import admin

from storybase.admin import StorybaseModelAdmin, StorybaseStackedInline
from storybase_help.models import HelpTranslation, Help

class HelpTranslationAdminForm(forms.ModelForm):
    class Meta:
        model = HelpTranslation
        fields = ['help', 'title', 'body']
        if 'tinymce' in settings.INSTALLED_APPS:
            from tinymce.widgets import TinyMCE
            widgets = {
               'body': TinyMCE(
                    attrs={'cols': 80, 'rows': 30},
                    mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top', 'plugins': 'table', 'theme_advanced_buttons3_add': 'tablecontrols', 'theme_advanced_statusbar_location': 'bottom', 'theme_advanced_resizing' : True},
                ),
            }


class HelpTranslationInline(StorybaseStackedInline):
    model = HelpTranslation
    form = HelpTranslationAdminForm
    extra = 1


class HelpAdmin(StorybaseModelAdmin):
    inlines = [HelpTranslationInline]
    prefix_inline_classes = ['HelpTranslationInline']
    readonly_fields = ['help_id']

admin.site.register(Help, HelpAdmin)
