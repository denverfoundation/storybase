"""Views"""

from django.views.generic.list import ListView

from storybase.views.generic import ModelIdDetailView
from storybase_user.models import Organization, Project

class OrganizationDetailView(ModelIdDetailView):
    """Display details about an Organization"""
    context_object_name = "organization"
    queryset = Organization.objects.all()


class OrganizationListView(ListView):
    """Display a list of all Organizations"""
    context_object_name = 'organizations'
    queryset = Organization.objects.all()


class ProjectDetailView(ModelIdDetailView):
    """Display details about a Project"""
    context_object_name = "project"
    queryset = Project.objects.all()

class ProjectListView(ListView):
    """Display a list of all Projects"""
    context_object_name = "projects"
    queryset = Project.objects.all()
