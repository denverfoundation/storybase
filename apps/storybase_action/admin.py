"""Django admin configuration for actions app"""

from django.contrib import admin
from storybase.admin import StorybaseModelAdmin

from storybase_action.models import SiteContactMessage

class SiteContactMessageAdmin(StorybaseModelAdmin):
    """Admin interface for SiteContactMessage model"""
    list_display = ('name', 'email', 'created')

admin.site.register(SiteContactMessage, SiteContactMessageAdmin)
