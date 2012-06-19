from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from storybase.admin import (StorybaseModelAdmin, StorybaseStackedInline)
from storybase_messaging.models import (SiteContactMessage, SystemMessage,
                                        SystemMessageTranslation)


class SiteContactMessageAdmin(StorybaseModelAdmin):
    """Admin interface for SiteContactMessage model"""
    list_display = ('name', 'email', 'created')


class SystemMessageTranslationInline(StorybaseStackedInline):
    """Inline for translated fields of a Story"""
    model = SystemMessageTranslation
    extra = 1


class SystemMessageAdmin(StorybaseModelAdmin):
    """Representation of Story model in the admin interface"""
    model = SystemMessage
    readonly_fields = ['created', 'last_edited']
    search_fields = ['systemmessagetranslation__title']
    list_display = ('obj_subject', 'created', 'sent')
    inlines = [SystemMessageTranslationInline]
    actions = ['send_message']
    prefix_inline_classes = ['SystemMessageTranslationInline']

    def obj_subject(self, obj):
        return obj.subject
    obj_subject.short_description = _("Subject") 

    def send_message(modeladmin, request, queryset):
        """
        Send messages via email.

        This is an admin action.

        """
        for message in queryset:
            message.send_notifications()
    send_message.short_description = "Send message"


admin.site.register(SiteContactMessage, SiteContactMessageAdmin)
admin.site.register(SystemMessage, SystemMessageAdmin)
