from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from categories.base import CategoryBaseAdmin

from storybase_taxonomy.forms import (CategoryAdminForm,
		                      CategoryTranslationAdminForm)
from storybase_taxonomy.models import Category, CategoryTranslation, Tag


class CategoryTranslationInline(admin.StackedInline):
    """Inline for translated fields of a Story"""
    model = CategoryTranslation
    form = CategoryTranslationAdminForm
    prepopulated_fields = {'slug': ('name',)}
    extra = 1


class CategoryAdmin(CategoryBaseAdmin):
    model = Category
    form = CategoryAdminForm
    list_display = ('obj_name',)
    search_fields = ('categorytranslation__name',)
    prepopulated_fields = {}
    inlines = [CategoryTranslationInline]

    def get_actions(self, request):
        """
        Override CategoryBaseAdmin's implementation because we want to
        allow bulk deletion
        """
        actions = super(CategoryBaseAdmin, self).get_actions(request)
        return actions

    def obj_name(self, obj):
        """
        Workaround to show the name in the change list view of the admin

        We need to do this because the name field is on the translation
        class

        """
        return obj.name
    obj_name.short_description = _('Name')


class TagAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
