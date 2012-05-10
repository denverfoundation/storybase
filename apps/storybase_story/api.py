"""REST API for Stories"""

from django.conf.urls.defaults import url

from haystack.query import SearchQuerySet

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization

from storybase_story.models import Story

class StoryResource(ModelResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title')
    summary = fields.CharField(attribute='summary')

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

	sqs = SearchQuerySet().models(Story)

        filter_fields = ['topics', 'projects', 'organizations']
	filters = {}
	for filter_field in filter_fields:
            sqs = sqs.facet(filter_field)
            filter_values = request.GET.get(filter_field, '').split(',')
	    if filter_values:
                filters['%s__in' % filter_field] = filter_values
	if filters:
            sqs = sqs.filter(**filters)

        objects = []

	for result in sqs.all():
            bundle = self.build_bundle(obj=result.object, request=request)
	    bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

	for filter_field, items in sqs.facet_counts()['fields'].iteritems():
            object_list[filter_field] = [item[0] for item in items]

        return self.create_response(request, object_list)
