
from tastypie.test import ResourceTestCase
from storybase_story.models import create_story
from storybase_badge.models import Badge


class BadgeResourceTest(ResourceTestCase):

    fixtures = ['denver_badges.json']

    def setUp(self):

        super(BadgeResourceTest, self).setUp()

        self.story = create_story(
            'Nature Remix'
        )

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

        badge = Badge.objects.all()[0]

        self.assertNotIn(badge, self.story.badges.all())

        self.api_client.patch('/api/0.1/badges/{}/'.format(badge.id), data={
            'stories': ['/api/0.1/stories/{}/'.format(self.story.story_id)]
        })

        self.assertIn(badge, self.story.badges.all())

    def test_remove_badge_from_story(self):

        badge = Badge.objects.all()[0]

        self.assertNotIn(self.story, badge.stories.all())
        badge.stories.add(self.story)
        self.assertIn(self.story, badge.stories.all())

        self.api_client.patch('/api/0.1/badges/{}/'.format(badge.id), data={
            'stories': []
        })

        self.assertNotIn(self.story, badge.stories.all())
