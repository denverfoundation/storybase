from django.contrib import admin
from storybase.admin import (StorybaseModelAdmin, StorybaseStackedInline,
        obj_title)
from cmsplugin_storybase.forms import NewsItemTranslationAdminForm
from cmsplugin_storybase.models import NewsItem, NewsItemTranslation

class NewsItemTranslationInline(StorybaseStackedInline):
    """Inline for translated fields of a NewsItem"""
    model = NewsItemTranslation
    form = NewsItemTranslationAdminForm 
    extra = 1


class NewsItemAdmin(StorybaseModelAdmin):
    list_display = (obj_title, 'author', 'last_edited', 'status')
    search_fields = ['name']
    readonly_fields = ['created', 'last_edited']
    inlines = [NewsItemTranslationInline,]
    prefix_inline_classes = ['NewsItemTranslationInline']

    def save_model(self, request, obj, form, change):
        """Perform pre-save operations and save the News Item 

        Sets the author field to the current user if it wasn't already set

        """
        if obj.author is None:
            obj.author = request.user
        obj.save()

admin.site.register(NewsItem, NewsItemAdmin)
