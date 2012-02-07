from django.conf.urls.defaults import *
from .views import google_login, google_logout, google_oauth2_callback

urlpatterns = patterns('',
    url(r'^google-login/$', google_login),
    url(r'^google-logout/$', google_logout),
    url(r'^google-oauth2-callback/$', google_oauth2_callback),
)
