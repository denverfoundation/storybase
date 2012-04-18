from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from storybase.admin import StorybaseModelAdmin, StorybaseStackedInline
from storybase_user.models import (Contact,
                                   Organization, OrganizationTranslation, 
                                   Project, ProjectStory, 
                                   ProjectTranslation)
   

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
        if getattr(obj, 'pk', None) is not None:
            # Object is not new
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


class OrganizationTranslationInline(StorybaseStackedInline):
    model = OrganizationTranslation 
    extra = 1


class OrganizationAdmin(StorybaseModelAdmin):
    search_fields = ['name']
    filter_horizontal = ['members']
    readonly_fields = ['created', 'last_edited', 'organization_id']
    inlines = [OrganizationTranslationInline,]
    prefix_inline_classes = ['OrganizationTranslationInline']

admin.site.register(Organization, OrganizationAdmin)


class ProjectTranslationInline(StorybaseStackedInline):
    model = ProjectTranslation 
    extra = 1


class ProjectStoryInline(admin.TabularInline):
    model = ProjectStory 
    extra = 0


class ProjectAdmin(StorybaseModelAdmin):
    search_fields = ['name']
    filter_horizontal = ['members', 'organizations']
    readonly_fields = ['created', 'last_edited', 'project_id']
    inlines = [ProjectStoryInline, ProjectTranslationInline]
    prefix_inline_classes = ['ProjectTranslationInline']

admin.site.register(Project, ProjectAdmin)

class ContactAdmin(StorybaseModelAdmin):
    pass

admin.site.register(Contact, ContactAdmin) 
