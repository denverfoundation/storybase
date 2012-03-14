from django import forms
from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE
from models import ExternalAsset, ExternalAssetTranslation, HtmlAsset, HtmlAssetTranslation, FilerImageAsset, FilerImageAssetTranslation

class AssetAdmin(admin.ModelAdmin):
    #list_display = ('title',)
    readonly_fields = ['asset_id']

class HtmlAssetTranslationAdminForm(forms.ModelForm):
    class Meta:
        model = HtmlAsset
        widgets = {
                'body': TinyMCE(
                    attrs={'cols': 80, 'rows': 30},
                    mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top'},
                )
        }

class HtmlAssetTranslationInline(admin.StackedInline):
    model = HtmlAssetTranslation
    form = HtmlAssetTranslationAdminForm
    extra = 1

class ExternalAssetTranslationInline(admin.StackedInline):
    model = ExternalAssetTranslation
    extra = 1

class FilerImageAssetTranslationInline(admin.StackedInline):
    model = FilerImageAssetTranslation
    extra = 1

class HtmlAssetAdmin(AssetAdmin):
    inlines = [HtmlAssetTranslationInline,]

class ExternalAssetAdmin(AssetAdmin):
    inlines = [ExternalAssetTranslationInline,]

class FilerImageAssetAdmin(AssetAdmin):
    inlines = [FilerImageAssetTranslationInline,]


admin.site.register(ExternalAsset, ExternalAssetAdmin)
admin.site.register(HtmlAsset, HtmlAssetAdmin)
admin.site.register(FilerImageAsset, FilerImageAssetAdmin)
