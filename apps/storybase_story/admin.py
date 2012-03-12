from django import forms
from django.contrib import admin
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from storybase_asset.models import Asset
from models import Story, Section, SectionAsset

class StoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ['title', 'author__first_name', 'author__last_name']
    list_filter = ('status', 'author', 'tags__name')
    filter_horizontal = ['assets']
    #form = make_ajax_form(Story, {'assets': 'asset'})

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "assets":
            kwargs["queryset"] = Asset.objects.filter(owner=request.user)
        return super(StoryAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

class SectionAssetInline(admin.TabularInline):
    model = SectionAsset
    # TODO: Fix this autocomplete
    # It fails because the default autocomplete tries to to filter
    # on the title of the Asset class which no longer exists after
    # I moved that to the translations.
    # See ajax_select.LookupChannel.get_query() to see where the 
    # call to filter() that breaks things is.
    # One solution might be to create a custom lookup class based
    # on the Translation model instead of the Asset model.
    # Another solution might be to add the Title field back to the
    # Asset model and have the save hook of the translation update
    # the related Asset's title.
    #form = make_ajax_form(SectionAsset, dict(asset='asset'))
    extra = 0

class SectionAdminForm(forms.ModelForm):
    children = forms.ModelMultipleChoiceField(
        queryset=Section.objects.all(),
        required=False)

    class Meta:
        model = Section

    def __init__(self, *args, **kwargs):
        super(SectionAdminForm, self).__init__(*args, **kwargs)

        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.fields['children'].queryset = Section.objects.filter(story=instance.story)

    def save(self, commit=True):
        model = super(SectionAdminForm, self).save(commit=False)

        # TODO: Handle Children field

        if commit:
            model.save()

        return model

class SectionAdmin(AjaxSelectAdmin):
    form = SectionAdminForm
    inlines = [SectionAssetInline,]

admin.site.register(Story, StoryAdmin)
admin.site.register(Section, SectionAdmin)
