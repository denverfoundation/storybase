from django import forms
from django.contrib import admin
from django.core import urlresolvers
from tinymce.widgets import TinyMCE
from storybase.admin import (StorybaseModelAdmin, StorybaseStackedInline)
from models import (Asset, 
    DataSet, DataSetTranslation, ExternalDataSet, LocalDataSet,
    ExternalAsset, ExternalAssetTranslation,
    HtmlAsset, HtmlAssetTranslation, 
    LocalImageAsset, LocalImageAssetTranslation)

class DefaultPublishedModelForm(forms.ModelForm):
    """ Model Form that sets the default status to published
    
    The default status for a model inheriting from PublishedModel is
    'draft', just to be safe and because, in code, we'll probably want to
    explicitly define the status.  However, in the Django admin, the
    default status for Assets should be 'published'.  This ModelForm
    is the workaround for setting the initial status to published.
    """
    def __init__(self, *args, **kwargs):
        super(DefaultPublishedModelForm, self).__init__(*args, **kwargs)
        self.fields['status'].initial = 'published'

class AssetAdmin(StorybaseModelAdmin):
    readonly_fields = ['asset_id']
    filter_horizontal = ['datasets']
    list_display = ('change_link', 'type', 'owner', 'last_edited')
    list_filter = ('type', 'owner')
    search_fields = ['asset__assettranslation__title']

    def change_link(self, obj):
        """
        Display the title of an Asset and a link to its change page 

        This is meant to be included in the class' list_display option.
       
        """
        # Get the subclass object so we can generate a link to the
        # subclass' change page and not the generic Asset one.
        # The generic Asset admin works, but doesn't show any of the
        # subclass-specific fields, which are most likely what we want
        # to edit.
        # TODO: See if the extra database query from get_subclass causes
        # problems with performance.
        subclass_obj = self.model.objects.get_subclass(pk=obj.pk)
        app_label = subclass_obj._meta.app_label
        module_name = subclass_obj._meta.module_name
        change_url = urlresolvers.reverse(
            "admin:%s_%s_change" % (app_label, module_name),
            args=(subclass_obj.pk,))
        # We call str(obj) instead of getting asset.title because we need
        # to auto-generate the title from the content in cases when the
        # asset doesn't have an explicitely-set title.
        return "<a href='%s'>%s</a>" % (change_url, str(subclass_obj))
    change_link.short_description = 'Title'
    change_link.allow_tags = True

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
                    mce_attrs={'theme': 'advanced', 'force_p_newlines': False, 'forced_root_block': '', 'theme_advanced_toolbar_location': 'top', 'plugins': 'table', 'theme_advanced_buttons3_add': 'tablecontrols'},
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

class HtmlAssetAdminForm(DefaultPublishedModelForm):
    class Meta:
        model = HtmlAsset

class HtmlAssetAdmin(AssetAdmin):
    form = HtmlAssetAdminForm
    inlines = [HtmlAssetTranslationInline,]
    prefix_inline_classes = ['HtmlAssetTranslationInline']

class ExternalAssetAdminForm(DefaultPublishedModelForm):
    class Meta:
        model = ExternalAsset

class ExternalAssetAdmin(AssetAdmin):
    form = ExternalAssetAdminForm
    inlines = [ExternalAssetTranslationInline,]
    prefix_inline_classes = ['ExternalAssetTranslationInline']

class LocalImageAssetAdminForm(DefaultPublishedModelForm):
    class Meta:
        model = LocalImageAsset

class LocalImageAssetAdmin(AssetAdmin):
    form = LocalImageAssetAdminForm
    inlines = [LocalImageAssetTranslationInline,]
    prefix_inline_classes = ['LocalImageAssetTranslationInline']

class DataSetTranslationInline(StorybaseStackedInline):
    model = DataSetTranslation
    extra = 1

class DataSetAdminForm(DefaultPublishedModelForm):
    class Meta:
        model = DataSet

class DataSetAdmin(StorybaseModelAdmin):
    form = DataSetAdminForm
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
