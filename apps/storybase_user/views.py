"""Views"""

from django.contrib.auth.decorators import login_required
from django.template import Context
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from storybase.views.generic import ModelIdDetailView
from storybase_user.models import Organization, Project

class AccountSummaryView(TemplateView):
    """Display user account information"""
    template_name = "storybase_user/account_summary.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AccountSummaryView, self).dispatch(*args, **kwargs)


class OrganizationDetailView(ModelIdDetailView):
    """Display details about an Organization"""
    context_object_name = "organization"
    queryset = Organization.objects.all()


class OrganizationListView(ListView):
    """Display a list of all Organizations"""
    context_object_name = 'organizations'
    queryset = Organization.objects.all().order_by('organizationtranslation__name')


class ProjectDetailView(ModelIdDetailView):
    """Display details about a Project"""
    context_object_name = "project"
    queryset = Project.objects.all()


class ProjectListView(ListView):
    """Display a list of all Projects"""
    context_object_name = "projects"
    queryset = Project.objects.all().order_by('-last_edited')


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
