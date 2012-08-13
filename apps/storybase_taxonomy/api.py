from django.conf.urls.defaults import url

from tastypie.authentication import Authentication
#from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from storybase.api import HookedModelResource, LoggedInAuthorization
from storybase_taxonomy.models import Tag

class TagResource(HookedModelResource):
    class Meta:
        always_return_data = True
        queryset = Tag.objects.all()
        resource_name = 'tags'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        detail_uri_name = 'tag_id'
        # Hide the underlying id
        excludes = ['id']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
        ]

    def get_related_object(self, id):
        try:
            story = Story.objects.get(story_id=story_id) 
            if not story.has_perm(request.user, 'change'):
                raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to change the story matching the provided story ID"))
        except ObjectDoesNotExist:
            raise ImmediateHttpResponse(response=http.HttpNotFound("A story matching the provided story ID could not be found"))

        return story

    def apply_request_kwargs(self, obj_list, request=None, **kwargs):
        story_id = kwargs.get('story_id')
        if story_id:
            story = self.get_related_object(story_id)
            return story.tags.all() 
        else:
            return obj_list

    def obj_create(self, bundle, request=None, **kwargs):
        story_id = kwargs.get('story_id')
        if story_id:
            story = self.get_related_obj(story_id)
            
        # Set the asset's owner to the request's user
        if request.user:
            kwargs['owner'] = request.user

        # Let the superclass create the object
        bundle = super(TagResource, self).obj_create(
            bundle, request, **kwargs)

        if story_id:
            # Associate the newly created object with the story
            story.locations.add(bundle.obj)
            story.save()

        return bundle
