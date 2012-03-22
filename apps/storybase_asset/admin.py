from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE
from storybase.admin import StorybaseModelAdmin, StorybaseStackedInline
from models import (Asset, 
    DataSet, DataSetTranslation, ExternalDataSet, LocalDataSet,
    ExternalAsset, ExternalAssetTranslation,
    HtmlAsset, HtmlAssetTranslation, 
    LocalImageAsset, LocalImageAssetTranslation)

class AssetAdmin(StorybaseModelAdmin):
    readonly_fields = ['asset_id']
    filter_horizontal = ['datasets']

    def save_model(self, request, obj, form, change):
        """ Sets the owner field to the current user if it wasn't already set """
        if obj.owner is None:
            obj.owner = request.user
        obj.save()

class HtmlAssetTranslationAdminForm(forms.ModelForm):
    class Meta:
        model = HtmlAsset
        widgets = {
                'body': TinyMCE(
                    attrs={'cols': 80, 'rows': 30},
                    mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top'},
                )
        }

class HtmlAssetTranslationInline(StorybaseStackedInline):
    model = HtmlAssetTranslation
    form = HtmlAssetTranslationAdminForm
    extra = 1

class ExternalAssetTranslationInline(StorybaseStackedInline):
    model = ExternalAssetTranslation
    extra = 1

class LocalImageAssetTranslationInline(StorybaseStackedInline):
    model = LocalImageAssetTranslation
    extra = 1

class HtmlAssetAdmin(AssetAdmin):
    inlines = [HtmlAssetTranslationInline,]
    prefix_inline_classes = ['HtmlAssetTranslationInline']

class ExternalAssetAdmin(AssetAdmin):
    inlines = [ExternalAssetTranslationInline,]
    prefix_inline_classes = ['ExternalAssetTranslationInline']

class LocalImageAssetAdmin(AssetAdmin):
    inlines = [LocalImageAssetTranslationInline,]
    prefix_inline_classes = ['LocalImageAssetTranslationInline']

class DataSetTranslationInline(StorybaseStackedInline):
    model = DataSetTranslation
    extra = 1

class DataSetAdmin(StorybaseModelAdmin):
    readonly_fields = ['dataset_id']
    inlines = [DataSetTranslationInline]
    prefix_inline_classes = ['DataSetTranslationInline']

    def save_model(self, request, obj, form, change):
        """ Sets the owner field to the current user if it wasn't already set """
        if obj.owner is None:
            obj.owner = request.user
        obj.save()

admin.site.register(Asset, AssetAdmin)
admin.site.register(ExternalAsset, ExternalAssetAdmin)
admin.site.register(HtmlAsset, HtmlAssetAdmin)
admin.site.register(LocalImageAsset, LocalImageAssetAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(ExternalDataSet, DataSetAdmin)
admin.site.register(LocalDataSet, DataSetAdmin)
