from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from models import Organization, Project

class StoryUserAdmin(UserAdmin):
    list_filter = UserAdmin.list_filter + ('groups__name',)

admin.site.unregister(User)
admin.site.register(User, StoryUserAdmin)

class OrganizationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    filter_horizontal = ['members']

admin.site.register(Organization, OrganizationAdmin)

class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    filter_horizontal = ['members']

admin.site.register(Project, ProjectAdmin)

