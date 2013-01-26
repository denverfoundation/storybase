"""Views"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django.template.loader import get_template, render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView 
from django.views.generic.list import ListView

from storybase.views.generic import ModelIdDetailView
from storybase.utils import full_url
from storybase_user.forms import (OrganizationModelForm, UserNotificationsForm,
        ProjectModelForm)
from storybase_user.auth.forms import ChangeUsernameEmailForm
from storybase_user.auth.utils import send_email_change_email
from storybase_user.models import (Organization, Project, UserProfile)
from storybase_user.utils import send_admin_mail


class AccountNotificationsView(UpdateView):
    model = UserProfile
    template_name = "storybase_user/account_notifications.html"
    form_class = UserNotificationsForm
    # TODO: When switching to Django 1.4 use reverse_lazy to 
    # get the URL of this view itself
    success_url = "/accounts/notifications/"

    def get_object(self, queryset=None):
        return self.request.user.get_profile()

    def form_valid(self, form):
        messages.success(self.request, _("Updated notification settings")) 
        return super(AccountNotificationsView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AccountNotificationsView, self).dispatch(*args, **kwargs)

class AccountStoriesView(TemplateView):
    template_name = "storybase_user/account_stories.html"

    def get_context_data(self, **kwargs):
      context = super(AccountStoriesView, self).get_context_data(**kwargs)
      context["stories_list"] = self.request.user.stories.exclude(status='deleted').order_by('-last_edited')
      return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AccountStoriesView, self).dispatch(*args, **kwargs)


class AccountSummaryView(TemplateView):
    """Display user account information"""
    template_name = "storybase_user/account_summary.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AccountSummaryView, self).dispatch(*args, **kwargs)

    def get_context_data(self, change_email_form=None, **kwargs):
        context = super(AccountSummaryView, self).get_context_data(**kwargs)
        if change_email_form is None:
            change_email_form = ChangeUsernameEmailForm(self.request.user)
        context['change_email_form'] = change_email_form 
        return context
    
    def post_change_email(self, request, *args, **kwargs):
        """Handle a POST request with the email change form submitted"""
        form = ChangeUsernameEmailForm(self.request.user, request.POST)
        if form.is_valid():
            messages.success(request, _("Your email address has been changed")) 
            user = form.save()
            # Send an email notification to the new email 
            send_email_change_email(user, user.email, request=self.request)
            # Send an email notification to the previous email
            send_email_change_email(user, form.previous_data['email'], request=self.request)
            return self.render_to_response(self.get_context_data())
        else:
            return self.render_to_response(self.get_context_data(change_email_form=form))

    def post(self, request, *args, **kwargs):
        """Handle a POST request
        
        This dispatches to different methods by checking a hidden
        input of the forms named ``form_id``.  You need to add this
        in the template for this view.
        
        """
        if 'form_id' in request.POST:
            if request.POST['form_id'] == 'change_email':
                return self.post_change_email(request, *args, **kwargs)
        return self.render_to_response(self.get_context_data())


class RelatedStoriesDetailView(ModelIdDetailView):
    """
    Base view for details of models with related stories
    
    Subclasses of this view are meant to be rendered with a template that 
    inherits from the ``storybase_user/detail_base.html`` template.

    """
    def get_story_list(self):
        """
        Return a list of stories that will be displayed in the view
        """
        return self.object.recent_stories()

    def get_story_list_title(self):
        """
        Return the title that will be displayed for the story list
        """
        return _("Recent Stories")

    def get_context_data(self, **kwargs):
        """Add related stories to template context"""
        context = super(RelatedStoriesDetailView, self).get_context_data(**kwargs)
        context['story_list'] = self.get_story_list()
        context['story_list_title'] = self.get_story_list_title()
        return context


class OrganizationDetailView(RelatedStoriesDetailView):
    """Display details about an Organization"""
    context_object_name = "organization"
    queryset = Organization.objects.all()


class OrganizationListView(ListView):
    """Display a list of all Organizations"""
    context_object_name = 'organizations'
    queryset = Organization.objects.filter(status='published').order_by('organizationtranslation__name')


class ProjectDetailView(RelatedStoriesDetailView):
    """Display details about a Project"""
    context_object_name = "project"
    queryset = Project.objects.all()


class ProjectListView(ListView):
    """Display a list of all Projects"""
    context_object_name = "projects"
    queryset = Project.objects.filter(status='published').order_by('-last_edited')


class UserProfileDetailView(RelatedStoriesDetailView):
    context_object_name = "profile"
    queryset = UserProfile.objects.all()

    def get_object_id_name(self):
        return 'profile_id'

    def get_story_list(self):
        """
        Return a list of stories that will be displayed in the view
        """
        return self.object.all_stories()

    def get_story_list_title(self):
        """
        Return the title that will be displayed for the story list
        """
        return _("Stories")


class ShareWidgetView(ModelIdDetailView):
    """
    Base view for Widget for sharing a project, organization or user
    """
    template_name = 'storybase_user/share_widget.html'


class OrganizationShareWidgetView(ShareWidgetView):
    model = Organization 


class ProjectShareWidgetView(ShareWidgetView):
    model = Project


class UserProfileShareWidgetView(ShareWidgetView):
    model = UserProfile

    def get_object_id_name(self):
        return 'profile_id'


class CreateStoryAggregatorView(CreateView):
    template_name = 'storybase_user/create_organization_project_base.html'

    def send_create_notification(self, obj=None):
        if obj is None:
            obj = self.object
        admin_url_name = "admin:%s_%s_change" % (obj._meta.app_label,
                obj._meta.object_name.lower())
        admin_url = full_url(reverse(admin_url_name, args=(obj.id,)))
        message = render_to_string('storybase_user/admin_approval_required_email.txt',
                { 'object': obj, 'admin_url': admin_url })
        subject = "New %s %s needs your approval" % (
                obj._meta.object_name, obj.name)
        send_admin_mail(subject, message, settings.DEFAULT_FROM_EMAIL)
        return True 

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateStoryAggregatorView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.status = 'pending'
        self.object = form.save()
        through_field_name = self.model._meta.object_name.lower()
        through_kwargs = {
            'user': self.request.user,
            through_field_name: self.object,
            'member_type': 'owner',
        }
        self.model.members.through.objects.create(**through_kwargs)
        # Send a notification to the admins that the object has been
        # created
        self.send_create_notification()
        # The default behavior is to redirect to the URL provided by 
        # self.get_success_url().  We just want to render a completed
        # message to the user via the template.
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(CreateStoryAggregatorView, self).get_context_data(**kwargs)
        context['model_name'] = self.model._meta.object_name
        context['list_url'] = reverse("%s_list" % (self.model._meta.object_name.lower()))
        return context


class CreateOrganizationView(CreateStoryAggregatorView):
    model = Organization
    form_class = OrganizationModelForm
    template_name = 'storybase_user/create_organization.html'


class CreateProjectView(CreateStoryAggregatorView):
    model = Project
    form_class = ProjectModelForm
    template_name = 'storybase_user/create_project.html'


@csrf_protect
@login_required
def password_change(request,
                    template_name='storybase_user/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    """
    Modified version of the default Django password change view
    
    This version defaults to this app's custom template, redirects back to the
    same view, and flashes a success message.

    """
    if post_change_redirect is None:
        post_change_redirect = reverse('storybase_user.views.password_change')
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            messages.success(request, _("Password changed")) 
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))


def simple_list(objects):
    """Render a simple listing of Projects or Organizations 
    
    Arguments:
    objects -- A queryset of Project or Organization model instances

    """
    template = get_template('storybase_user/simple_list.html')
    context =  Context({"objects": objects})
    return template.render(context)


def homepage_organization_list(count):
    """Render a listing of organizations for the homepage"""
    orgs = Organization.objects.on_homepage().order_by('-last_edited')[:count]
    return simple_list(orgs)


def homepage_project_list(count):
    """Render a listing of projects for the homepage"""
    projects = Project.objects.on_homepage().order_by('-last_edited')[:count]
    return simple_list(projects)
