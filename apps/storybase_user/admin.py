import csv
import datetime

from django import forms
from django.conf import settings
from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from storybase.admin import (StorybaseModelAdmin, StorybaseStackedInline,
                             toggle_featured)
from storybase_story.models import Story
from storybase_badge.models import Badge
from storybase_user.auth.utils import send_account_deactivate_email
from storybase_user.models import (Organization, OrganizationTranslation, 
        OrganizationMembership, Project, ProjectStory, ProjectTranslation,
        ProjectMembership, UserProfile)
                                  
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
    badges = forms.ModelMultipleChoiceField(
        queryset=Badge.objects.all(),
        required=False)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False
    fieldsets = (
        (
             _('Notifications'), 
             {
                 'fields': ('notify_admin', 'notify_digest', 'notify_story_unpublished', 'notify_story_published', 'notify_story_comment'),
                 'description': _("Users will receive emails about these kind of events"),
             }
        ),
    )
    

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
        ('Badges', {'fields': ('badges',)}),
    )

    inlines = [UserProfileInline]

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
            obj.get_profile().badges.clear()
            for organization in form.cleaned_data['organizations']:
                OrganizationMembership.objects.create(user=obj,
                        organization=organization)
            for project in form.cleaned_data['projects']:
                ProjectMembership.objects.create(user=obj,
                        project=project)
            for story in form.cleaned_data['stories']:
                obj.stories.add(story)
            for badge in form.cleaned_data['badges']:
                obj.get_profile().badges.add(badge)

        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form.base_fields['organizations'].initial = obj.organizations.all()
            self.form.base_fields['badges'].initial = obj.get_profile().badges.all()
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
        # TODO: Figure out if there's any good reason why I imported
        # these locallly
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
        for user in queryset:
            send_account_deactivate_email(user, request=request)
        self.message_user(request, "Deactivated user(s)")
    set_inactive.short_description = "Deactivate user"

    def get_urls(self):
        urls = super(StoryUserAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^csv/$', self.csv_view)
        )
        return my_urls + urls

    def csv_view(self, request):
        def encode(obj, field_name):
            return unicode(getattr(obj, field_name)).encode("utf-8","replace")

        def encode_field_verbose_name(klass, field_name):
            return capfirst(unicode(klass._meta.get_field(field_name).verbose_name).encode("utf-8","replace"))

        def header_row(user_field_names, profile_field_names):
            row = [encode_field_verbose_name(User, field_name) for field_name in user_field_names]
            row.extend([encode_field_verbose_name(UserProfile, field_name) for field_name in profile_field_names])
            return row

        queryset = self.queryset(request)
        filename = "userinfo_%s.csv" % (datetime.date.today().strftime("%Y%m%d"))
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
        user_field_names = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'last_login',)
        # TODO: See if I can use methods of the modeladmin as fields
        profile_field_names = ('notify_admin', 'notify_digest',
            'notify_story_unpublished', 'notify_story_published',
            'notify_story_comment')
        writer = csv.writer(response)
        writer.writerow(header_row(user_field_names, profile_field_names))
        for obj in queryset:
            profile = obj.get_profile()
            row = [encode(obj, field_name) for field_name in user_field_names]
            row.extend([encode(profile, field_name) for field_name in profile_field_names])
            writer.writerow(row)
        return response


admin.site.unregister(User)
admin.site.register(User, StoryUserAdmin)


class OrganizationTranslationInline(StorybaseStackedInline):
    model = OrganizationTranslation 
    extra = 1


class OrganizationMembershipInline(admin.TabularInline):
    model = Organization.members.through
    extra = 0


class OrganizationAdmin(StorybaseModelAdmin):
    search_fields = ['organizationtranslation__name']
    filter_horizontal = ['members', 'featured_assets']
    readonly_fields = ['created', 'last_edited', 'organization_id']
    inlines = [OrganizationTranslationInline, OrganizationMembershipInline]
    prefix_inline_classes = ['OrganizationTranslationInline']

admin.site.register(Organization, OrganizationAdmin)


class ProjectTranslationInline(StorybaseStackedInline):
    model = ProjectTranslation 
    extra = 1


class ProjectStoryInline(admin.TabularInline):
    model = ProjectStory 
    extra = 0


class ProjectMembershipInline(admin.TabularInline):
    model = Project.members.through
    extra = 0


class ProjectAdmin(StorybaseModelAdmin):
    search_fields = ['projecttranslation__name']
    filter_horizontal = ['members', 'organizations', 'featured_assets']
    list_filter = ('on_homepage',)
    readonly_fields = ['created', 'last_edited', 'project_id']
    inlines = [ProjectMembershipInline, ProjectStoryInline, 
            ProjectTranslationInline]
    prefix_inline_classes = ['ProjectTranslationInline']
    actions = [toggle_featured]


admin.site.register(Project, ProjectAdmin)
