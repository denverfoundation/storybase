from django import forms
from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE
from models import ExternalAsset, FilerImageAsset, HtmlAsset

class AssetAdmin(admin.ModelAdmin):
    list_display = ('title',)

class HtmlAssetAdminForm(forms.ModelForm):
    class Meta:
        model = HtmlAsset
        widgets = {
                'body': TinyMCE(
                    attrs={'cols': 80, 'rows': 30},
                    mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top'},
                )
        }

class HtmlAssetAdmin(AssetAdmin):
    form = HtmlAssetAdminForm
    """
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE},
    }
    """

admin.site.register(ExternalAsset, AssetAdmin)
admin.site.register(HtmlAsset, HtmlAssetAdmin)
admin.site.register(FilerImageAsset, AssetAdmin)
