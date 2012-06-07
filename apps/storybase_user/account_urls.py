"""
URL Configuration for views dealing with account management

These are broken out into a separate URLconf as they are likely to be attached
at a different root than the other URL patterns. 

"""

from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset

from storybase_user.views import AccountSummaryView

urlpatterns = patterns('',
    url(r'^$', AccountSummaryView.as_view(),
	name='account_summary'),
    url(r'^password/reset$', password_reset, name='password_reset'),
)
