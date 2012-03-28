from django.contrib import admin
#from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
#from ajax_select import make_ajax_form
#from ajax_select.admin import AjaxSelectAdmin
from storybase.admin import (StorybaseModelAdmin, StorybaseStackedInline,
    obj_title)
from storybase_asset.models import Asset
from models import (Story, StoryTranslation,
    Section, SectionTranslation, SectionAsset, SectionRelation)        

class StoryTranslationInline(StorybaseStackedInline):
    model = StoryTranslation
    extra = 1
    prepopulated_fields = {"slug": ("title",)}

class StoryAdmin(StorybaseModelAdmin):
    readonly_fields = ['story_id', 'created', 'last_edited']
    search_fields = ['storytranslation__title', 'author__first_name', 'author__last_name']
    list_display = (obj_title, 'author', 'last_edited', 'status')
    list_filter = ('status', 'author')
    filter_horizontal = ['assets', 'projects', 'organizations']
    inlines = [StoryTranslationInline]
    prefix_inline_classes = ['StoryTranslationInline']

    def save_model(self, request, obj, form, change):
        """ Sets the author field to the current user if it wasn't already set """
        if obj.author is None:
            obj.author = request.user
        obj.save()

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

class SectionTranslationInline(StorybaseStackedInline):
    model = SectionTranslation
    extra = 1

def section_story_title(obj):
    """ Callable to return a Section's Story's title in the Django admin """
    return obj.story.title
section_story_title = 'Story Title'

# TODO: Enable this on switch to Django 1.4
#class SectionStoryTitleListFilter(SimpleListFilter):
#    title = _('story title') 
#    parameter_name = 'title'
#
#    def lookups(self, request, model_admin):
#        qs = model_admin.queryset(request)
#        values = qs.values('pk', 'story__storytranslation__title').distinct()
#        return [(value['pk'], value['story_storytranslation__title']) for value in values]
#
#    def queryset(self, request, queryset):
#        return queryset.filter(pk=self.value())

#class SectionAdmin(AjaxSelectAdmin):
class SectionAdmin(StorybaseModelAdmin):
    inlines = [SectionTranslationInline, SectionAssetInline]
    prefix_inline_classes = ['SectionTranslationInline']
    list_display = (obj_title, 'root')
# TODO: Enable this on switch to Django 1.4
#    list_filter = (SectionStoryTitleListFilter, 'root')
    list_filter = ('story__storytranslation__title', 'root')
    search_fields = ['sectiontranslation__title']
    readonly_fields = ['section_id']

admin.site.register(Story, StoryAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionRelation, admin.ModelAdmin)
