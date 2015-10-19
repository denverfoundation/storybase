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

        self.user_authorized = User.objects.create_user('wilbertom', 'wilbertom@pr.com', 'filoteo_muy_elegante')
        self.user_authorized.userprofile.badges.add(self.badge)
        self.user_authorized.save()

    def get_credentials(self):
        return self.create_basic(username=self.user_authorized.username, password=self.user_authorized.password)


    def test_get_list_of_badges(self):

        response = self.api_client.get('/api/0.1/badges/', format='json')
        self.assertValidJSONResponse(response)

        objects = self.deserialize(response)['objects']

        self.assertEquals(len(objects), 5)
        self.assertEquals(objects[0], {
            u'description': u'Stories promoted by the Denver Foundation Staff.',
            u'icon_uri': '/static/img/badges/denver-foundation.png',
            u'id': 1,
            u'name': u'Denver Foundation',
            u'resource_uri': '/api/0.1/badges/1/',
            u'stories': []
        })

    def test_badge_details(self):
        self.assertValidJSONResponse(self.api_client.get(self.badge_uri))

    def test_posting(self):
        self.assertHttpMethodNotAllowed(self.api_client.post(
            self.badge_uri,
            data={},
            authentication=self.get_credentials()
        ))

        self.assertHttpMethodNotAllowed(self.api_client.post(
            '/api/0.1/badges/',
            data={},
            authentication=self.get_credentials()
        ))

    def test_putting(self):
        self.assertHttpMethodNotAllowed(
            self.api_client.post(self.badge_uri, data={}, authentication=self.get_credentials())
        )

    def test_deleting(self):
        self.assertHttpMethodNotAllowed(self.client.delete(self.badge_uri, authentication=self.get_credentials()))

    def test_add_badge_to_story(self):

        self.assertNotIn(self.badge, self.story.badges.all())

        self.api_client.patch(self.badge_uri, data={
            'stories': [self.story_uri]
        }, authentication=self.get_credentials())

        self.assertIn(self.badge, self.story.badges.all())

    def test_remove_badge_from_story(self):

        self.assertNotIn(self.story, self.badge.stories.all())
        self.badge.stories.add(self.story)
        self.assertIn(self.story, self.badge.stories.all())

        response = self.api_client.patch(self.badge_uri, data={
            'stories': []
        }, authentication=self.get_credentials())

        self.assertHttpOK(response)

        self.assertNotIn(self.story, self.badge.stories.all())

    def test_user_can_edit_badge(self):
        user = User.objects.create_user('Nicky Jam', 'nicky@gmail.com', 'el_perdon')
        user.save()
        profile = user.userprofile
        self.assertFalse(profile.can_edit_badge(self.badge))
        profile.badges.add(self.badge)
        self.assertTrue(profile.can_edit_badge(self.badge))

    def test_edit_badge_from_story_unauthorized(self):

        new_user = User.objects.create_user('centro', 'hacker@pr.com', 'filoteo_muy_elegante')
        new_user.save()
        profile = new_user.userprofile

        response = self.api_client.patch(self.badge_uri, data={
            'stories': []
        })

        self.assertHttpUnauthorized(response)

        self.api_client.client.login(username=new_user.username, password=new_user.password)

        response = self.api_client.patch(self.badge_uri, data={
            'stories': []
        })

        self.assertHttpUnauthorized(response)

        profile.badges.add(self.badge)
        profile.save()

        self.assertTrue(profile.can_edit_badge(self.badge))
        self.api_client.client.login(username=new_user.username, password=new_user.password)

        response = self.api_client.patch(self.badge_uri, data={
            'stories': []
        })

        self.assertHttpOK(response)
