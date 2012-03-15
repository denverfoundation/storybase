from django.views.generic import DetailView
from models import Organization

class OrganizationDetailView(DetailView):

    context_object_name = "organization"
    queryset = Organization.objects.all()

    def get_object(self):
        object = self.queryset.get(organization_id=self.kwargs['organization_id'])
        return object
