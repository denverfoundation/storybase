from django.conf.urls import url, patterns
from .views import BadgesView

urlpatterns = patterns(
    '',
    url(r'^badges/$', BadgesView.as_view(), name='badges')
)