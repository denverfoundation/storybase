
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.resources import ModelResource
from tastypie import fields

from storybase_badge.models import Badge


class BadgeResource(ModelResource):

    stories = fields.ToManyField('storybase_story.api.StoryResource', 'stories', full=False)

    class Meta:
        authorization = Authorization()
        authentication = Authentication()
        queryset = Badge.objects.all()
        resource_name = 'badges'
