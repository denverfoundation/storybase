from django.conf.urls.defaults import *
from views import OrganizationDetailView

urlpatterns = patterns('',
    url(r'organizations/(?P<organization_id>[0-9a-f]{32,32})/$', OrganizationDetailView.as_view(), name='organization_detail'), 
)
