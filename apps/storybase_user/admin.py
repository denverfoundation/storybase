from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class StoryUserAdmin(UserAdmin):
    list_filter = UserAdmin.list_filter + ('groups__name',)

admin.site.unregister(User)
admin.site.register(User, StoryUserAdmin)
