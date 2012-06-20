from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from storybase.admin import StorybaseModelAdmin, StorybaseStackedInline
from storybase_story.models import Story
from storybase_user.models import (Organization, OrganizationTranslation, 
                                   Project, ProjectStory, 
                                   ProjectTranslation)

if 'social_auth' in settings.INSTALLED_APPS:
    import social_auth
else:
    social_auth = None

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
    stories = forms.ModelMultipleChoiceField(
        queryset=Story.objects.all(),
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
        (_('Stories'), {'fields': ('stories',)}),
    )

    list_filter = UserAdmin.list_filter + ('groups__name',)
    list_display = UserAdmin.list_display + ('is_active',)
    if social_auth:
        list_display = list_display + ('social_accounts',)
    actions = ['send_password_reset_emails', 'set_inactive']

    def save_model(self, request, obj, form, change):  
        if getattr(obj, 'pk', None) is not None:
            # Object is not new
            obj.organizations.clear()
            obj.projects.clear()
            obj.stories.clear()
            for organization in form.cleaned_data['organizations']:
                obj.organizations.add(organization)
            for project in form.cleaned_data['projects']:
                obj.projects.add(project)
            for story in form.cleaned_data['stories']:
                obj.stories.add(story)

        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form.base_fields['organizations'].initial = obj.organizations.all()
            self.form.base_fields['projects'].initial = obj.projects.all()
            self.form.base_fields['stories'].queryset = obj.stories.all()
            self.form.base_fields['stories'].initial = obj.stories.all()
        return super(StoryUserAdmin, self).get_form(request, obj)

    def social_accounts(self, obj):
        """Return a list of federated login accounts created with social_auth"""
        auth_accounts = []
        if social_auth:
            auth_accounts = [user_auth.provider for user_auth in obj.social_auth.all()]
        return ", ".join(auth_accounts)

    def send_password_reset_emails(self, request, queryset):
        """Send a password reset email to users
        
        This is an admin action.
        """
        from storybase.context_processors import conf
        from storybase_user.auth.utils import send_password_reset_email
        
        for user in queryset:
            send_password_reset_email(user, request=request, 
                                      extra_context=conf(request))
        self.message_user(request, "Password reset email sent")
    send_password_reset_emails.short_description = "Send password reset email"


    def set_inactive(self, request, queryset):
        """Set a user account to be inactive"""
        queryset.update(is_active=False)
        self.message_user(request, "Deactivated user(s)")
    set_inactive.short_description = "Deactivate user"

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
