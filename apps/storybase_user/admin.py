from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from storybase.admin import StorybaseModelAdmin
from models import Organization, Project

class StoryUserAdminForm(UserChangeForm):
    """ 
    Custom form for editing users in the Django admin

    This adds fields for the ManyToMany relations to Organization and 
    Project models.  These aren't included automatically because they're
    the relation is defined on Organization and Project, not on User
    """
    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        required=False)
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        required=False)

class StoryUserAdmin(UserAdmin):
    """
    Custom admin for Users

    Adds a filter in list view on Group name and uses the custom form
    that allows editing of Organization and Project relations.
    """
    form = StoryUserAdminForm
    # Add additional fieldsets so that our custom form fields are displayed
    fieldsets = (
        # These are the default fieldsets
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Groups'), {'fields': ('groups',)}),
        # These are the custom fieldsets
        (_('Organizations'), {'fields': ('organizations',)}),
        (_('Projects'), {'fields': ('projects',)}),
    )

    list_filter = UserAdmin.list_filter + ('groups__name',)

    def save_model(self, request, obj, form, change):  
        obj.organizations.clear()
        obj.projects.clear()
        for organization in form.cleaned_data['organizations']:
            obj.organizations.add(organization)
        for project in form.cleaned_data['projects']:
            obj.projects.add(project)
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form.base_fields['organizations'].initial = obj.organizations.all()
            self.form.base_fields['projects'].initial = obj.projects.all()
        return super(StoryUserAdmin, self).get_form(request, obj)

admin.site.unregister(User)
admin.site.register(User, StoryUserAdmin)

class OrganizationAdmin(StorybaseModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    filter_horizontal = ['members']
    readonly_fields = ['created', 'last_edited', 'organization_id']

admin.site.register(Organization, OrganizationAdmin)

class ProjectAdmin(StorybaseModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    filter_horizontal = ['members', 'organizations']
    readonly_fields = ['project_id']

admin.site.register(Project, ProjectAdmin)

