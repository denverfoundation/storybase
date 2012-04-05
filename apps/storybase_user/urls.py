from django.conf.urls.defaults import *
from views import OrganizationDetailView, ProjectDetailView

urlpatterns = patterns('',
    url(r'organizations/(?P<organization_id>[0-9a-f]{32,32})/$',
	OrganizationDetailView.as_view(), name='organization_detail_by_id'), 
    url(r'organizations/(?P<slug>[0-9a-z-]+)/$',
        OrganizationDetailView.as_view(), name='organization_detail'), 
    url(r'projects/(?P<project_id>[0-9a-f]{32,32})/$',
	ProjectDetailView.as_view(), name='project_detail_by_id'), 
    url(r'projects/(?P<slug>[0-9a-z-]+)/$',
	ProjectDetailView.as_view(), name='project_detail'), 
)
