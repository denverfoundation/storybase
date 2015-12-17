from django.conf import settings
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist

from tastypie import http
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.utils import trailing_slash

from storybase.api import HookedModelResource, LoggedInAuthorization
from storybase_story.models import Story
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
        filtering = {
            'name': ('exact', 'startswith', 'istartswith'),
        }

    def prepend_urls(self):
        subs = (self._meta.resource_name, settings.UUID_PATTERN, trailing_slash())
        return [
            url(r"^(?P<resource_name>{})/stories/(?P<story_id>{}){}$".format(*subs),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list",
            ),
            url(r"^(?P<resource_name>{0})/(?P<tag_id>{1})/stories/(?P<story_id>{1}){2}$".format(*subs),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail",
            ),
        ]

    def get_related_object(self, request, **kwargs):
        try:
            story_id = kwargs.get('story_id')
            story = Story.objects.get(story_id=story_id)
            if not story.has_perm(request.user, 'change'):
                raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to change the story matching the provided story ID"))
        except ObjectDoesNotExist:
            raise ImmediateHttpResponse(response=http.HttpNotFound("A story matching the provided story ID could not be found"))

        return story

    def apply_request_kwargs(self, obj_list, bundle, **kwargs):
        story_id = kwargs.get('story_id')
        if story_id:
            story = self.get_related_object(bundle.request, **kwargs)
            return story.tags.all()
        else:
            return obj_list

    def obj_create(self, bundle, **kwargs):
        story_id = kwargs.get('story_id')
        if story_id:
            story = self.get_related_object(bundle.request, **kwargs)

        tag_id = bundle.data.get('tag_id')
        if tag_id:
            # Existing tag, don't create it, just retrieve it
            try:
                bundle.obj = self.obj_get(bundle, tag_id=tag_id)
            except ObjectDoesNotExist:
                pass
        else:
            # Let the superclass create the object
            bundle = super(TagResource, self).obj_create(bundle, **kwargs)

        if story_id:
            # Associate the retrieved or newly created object with the story
            story.tags.add(bundle.obj)
            story.save()

        return bundle

    def obj_delete(self, bundle, **kwargs):
        obj = kwargs.pop('_obj', None)

        story_id = kwargs.get('story_id')
        if story_id:
            story = self.get_related_object(bundle.request, **kwargs)
            kwargs.pop('story_id')

            if not hasattr(obj, 'delete'):
                try:
                    obj = self.obj_get(bundle, **kwargs)
                except ObjectDoesNotExist:
                    raise NotFound("A model instance matching the provided arguments could not be found.")
            story.tags.remove(obj)
            story.save()
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to delete a tag, only to remove them from a story"))
