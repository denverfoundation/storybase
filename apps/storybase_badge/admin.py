
from django.contrib import admin
from storybase_badge.models import Badge


class BadgeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Badge, BadgeAdmin)
