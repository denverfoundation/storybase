"""Views"""

from storybase.views.generic import ModelIdDetailView
from storybase_user.models import Organization, Project

class OrganizationDetailView(ModelIdDetailView):

    context_object_name = "organization"
    queryset = Organization.objects.all()


class ProjectDetailView(ModelIdDetailView):

    context_object_name = "project"
    queryset = Project.objects.all()
