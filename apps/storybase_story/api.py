"""REST API for Stories"""

from django.conf.urls.defaults import url

from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization

from storybase_story.models import Story

class StoryResource(ModelResource):
    class Meta:
        queryset = Story.objects.filter(status__exact='published')
        resource_name = 'stories'
        allowed_methods = ['get']
	# Allow open access to this resource for now since it's read-only
        authentication = Authentication()
	authorization = ReadOnlyAuthorization()

    def override_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/explore%s$'  % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_explore'), name="api_get_explore"),
        ]

    def get_explore(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
