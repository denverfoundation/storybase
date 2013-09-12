from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from cms.admin.forms import PageForm
from cms.admin.pageadmin import PageAdmin
from cms.models import Page
from cms.utils import get_language_from_request
from storybase.admin import (StorybaseModelAdmin, StorybaseStackedInline,
        obj_title)
from cmsplugin_storybase.forms import (ActivityTranslationAdminForm, 
    NewsItemTranslationAdminForm)
from cmsplugin_storybase.models import (Activity, ActivityTranslation,
    NewsItem, NewsItemTranslation, Teaser, EmptyTeaser)
    

class ActivityTranslationInline(StorybaseStackedInline):
    model = ActivityTranslation
    form = ActivityTranslationAdminForm
    extra = 1


class ActivityAdmin(StorybaseModelAdmin):
    list_display = (obj_title,)
    search_fields = ['activitytranslation__title',]
    inlines = [ActivityTranslationInline,]
    prefix_inline_classes = ['ActivityTranslationInline',]


class NewsItemTranslationInline(StorybaseStackedInline):
    """Inline for translated fields of a NewsItem"""
    model = NewsItemTranslation
    form = NewsItemTranslationAdminForm 
    extra = 1


class NewsItemAdmin(StorybaseModelAdmin):
    list_display = (obj_title, 'author', 'last_edited', 'status',
            'on_homepage')
    list_filter = ('status', 'author', 'on_homepage')
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


class StorybasePageForm(PageForm):
    """Custom PageForm to handle the Teaser"""
    teaser = forms.CharField(label=_("Page Teaser"), 
        widget=forms.Textarea,
        help_text=_("Brief description of the page to be included on parent pages"),
        required=False)


class StorybasePageAdmin(PageAdmin):
    """Custom PageAdmin to handle our Teaser"""
    form = StorybasePageForm

    def get_form(self, request, obj=None, **kwargs):
        language = get_language_from_request(request, obj)

        if obj:
            form = super(StorybasePageAdmin, self).get_form(request, obj, **kwargs)
        else:
            form = StorybasePageForm

        if obj:
            try:
                teaser_obj = obj.teaser_set.get(language=language)
            except:
                teaser_obj = EmptyTeaser()

            form.base_fields['teaser'].initial = teaser_obj.teaser
        else:
            form.base_fields['teaser'].initial = u''

        return form

    def save_model(self, request, obj, form, change):
        # Call super to save the page and title
        super(StorybasePageAdmin, self).save_model(request, obj, form, change)

        # Now, save our teaser
        language = form.cleaned_data['language']
        teaser_obj, created = Teaser.objects.get_or_create(page=obj, language=language)
        teaser_obj.teaser = form.cleaned_data['teaser']
        teaser_obj.save()


def update_fieldsets(cls):
    """Add our custom fields to the Admin fieldsets"""
    cls.fieldsets[0][1]['fields'].append('teaser')


update_fieldsets(StorybasePageAdmin)


admin.site.register(Activity, ActivityAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
# Replace the default PageAdmin class with our own
admin.site.unregister(Page)
admin.site.register(Page, StorybasePageAdmin)
