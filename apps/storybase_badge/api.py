
from tastypie.authorization import ReadOnlyAuthorization, Unauthorized
from tastypie.authentication import Authentication
from tastypie.resources import ModelResource
from tastypie import fields

from storybase.api.authorization import UserAuthorization
from storybase_badge.models import Badge


class BadgeAuthorization(ReadOnlyAuthorization, UserAuthorization):

    def update_detail(self, object_list, bundle):

        if self.user_valid(bundle) and bundle.request.user.get_profile().can_edit_badge(bundle.obj):
            return True
        else:
            raise Unauthorized()


class BadgeResource(ModelResource):

    stories = fields.ToManyField('storybase_story.api.StoryResource', 'stories', full=False)

    class Meta:
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'patch']
        authentication = Authentication()
        authorization = BadgeAuthorization()
        queryset = Badge.objects.all()
        resource_name = 'badges'

