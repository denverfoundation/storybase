from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from storybase_story.models import create_story
from storybase_badge.models import Badge


class BadgeResourceTest(ResourceTestCase):

    fixtures = ['denver_badges.json']

    def setUp(self):

        super(BadgeResourceTest, self).setUp()

        self.story = create_story('Nature Remix')
        self.story_uri = '/api/0.1/stories/{}/'.format(self.story.story_id)

        self.story2 = create_story('Learning How to Stand up')
        self.story_uri2 = '/api/0.1/stories/{}/'.format(self.story2.story_id)

        self.badge = Badge.objects.all()[0]
        self.badge_uri = '/api/0.1/badges/{}/'.format(self.badge.id)

    def test_get_list_of_badges(self):

        response = self.api_client.get('/api/0.1/badges/', format='json')
        self.assertValidJSONResponse(response)

        objects = self.deserialize(response)['objects']

        self.assertEquals(objects[0], {
            u'description': u'Stories promoted by the Denver Foundation Staff.',
            u'icon_uri': '/static/img/badges/denver-foundation.png',
            u'id': 1,
            u'name': u'Denver Foundation',
            u'resource_uri': '/api/0.1/badges/1/',
            u'stories': []
        })

    def test_add_badge_to_story(self):

        self.assertNotIn(self.badge, self.story.badges.all())

        self.api_client.patch(self.badge_uri, data={
            'stories': [self.story_uri]
        })

        self.assertIn(self.badge, self.story.badges.all())

    def test_remove_badge_from_story(self):

        self.assertNotIn(self.story, self.badge.stories.all())
        self.badge.stories.add(self.story)
        self.assertIn(self.story, self.badge.stories.all())

        self.api_client.patch(self.badge_uri, data={
            'stories': []
        })

        self.assertNotIn(self.story, self.badge.stories.all())

