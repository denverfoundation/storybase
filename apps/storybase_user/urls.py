try:
    import shortuuid
except ImportError:
    shortuuid = None

from django.conf.urls.defaults import *
from storybase_user.views import (OrganizationDetailView, OrganizationListView,
    OrganizationShareWidgetView, ProjectDetailView, ProjectListView,
    ProjectShareWidgetView, UserProfileDetailView, UserProfileShareWidgetView)
   
urlpatterns = patterns('',
    url(r'organizations/$', OrganizationListView.as_view(),
        name='organization_list'),
    url(r'organizations/(?P<organization_id>[0-9a-f]{32,32})/$',
        OrganizationDetailView.as_view(), name='organization_detail_by_id'),
    url(r'organizations/(?P<slug>[0-9a-z-]+)/$',
        OrganizationDetailView.as_view(), name='organization_detail'),
    url(r'organizations/(?P<organization_id>[0-9a-f]{32,32})/share-widget/$',
        OrganizationShareWidgetView.as_view(),
        name='organization_share_widget'),
    url(r'organizations/(?P<slug>[0-9a-z-]+)/share-widget/$',
        OrganizationShareWidgetView.as_view(),
        name='organization_share_widget'),
    url(r'projects/$', ProjectListView.as_view(), name='project_list'),
    url(r'projects/(?P<project_id>[0-9a-f]{32,32})/$',
        ProjectDetailView.as_view(), name='project_detail_by_id'), 
    url(r'projects/(?P<slug>[0-9a-z-]+)/$',
        ProjectDetailView.as_view(), name='project_detail'), 
    url(r'projects/(?P<project_id>[0-9a-f]{32,32})/share-widget/$',
        ProjectShareWidgetView.as_view(), name='project_share_widget'), 
    url(r'projects/(?P<slug>[0-9a-z-]+)/share-widget/$',
        ProjectShareWidgetView.as_view(), name='project_share_widget'), 
    url(r'users/(?P<profile_id>[0-9a-f]{32,32})/$', 
        UserProfileDetailView.as_view(), name='userprofile_detail'),
    url(r'users/(?P<profile_id>[0-9a-f]{32,32})/share-widget/$', 
        UserProfileShareWidgetView.as_view(),
        name='userprofile_share_widget'),
)

if shortuuid:
    alphabet = shortuuid.get_alphabet()
    urlpatterns = urlpatterns + patterns('',
        url(r"users/(?P<short_profile_id>[%s]+)/$" % (alphabet), 
            UserProfileDetailView.as_view(), name='userprofile_detail'),
        url(r"users/(?P<short_profile_id>[%s]+)/share-widget/$" % (alphabet), 
            UserProfileShareWidgetView.as_view(),
            name='userprofile_share_widget'),
    )
