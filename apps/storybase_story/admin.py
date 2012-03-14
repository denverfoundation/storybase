from django.contrib import admin
#from ajax_select import make_ajax_form
#from ajax_select.admin import AjaxSelectAdmin
from storybase_asset.models import Asset
from models import Story, Section, SectionAsset, SectionRelation

class StoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['story_id']
    search_fields = ['title', 'author__first_name', 'author__last_name']
    list_filter = ('status', 'author')
    filter_horizontal = ['assets']

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

#class SectionAdmin(AjaxSelectAdmin):
class SectionAdmin(admin.ModelAdmin):
    inlines = [SectionAssetInline]
    list_filter = ('story__title',)
    search_fields = ['title']
    readonly_fields = ['section_id']

admin.site.register(Story, StoryAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionRelation, admin.ModelAdmin)
