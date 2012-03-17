from django.views.generic import DetailView
from models import Organization, Project

class OrganizationDetailView(DetailView):

    context_object_name = "organization"
    queryset = Organization.objects.all()

    def get_object(self):
        object = self.queryset.get(organization_id=self.kwargs['organization_id'])
        return object

class ProjectDetailView(DetailView):

    context_object_name = "project"
    queryset = Project.objects.all()

    def get_object(self):
        object = self.queryset.get(project_id=self.kwargs['project_id'])
        return object
