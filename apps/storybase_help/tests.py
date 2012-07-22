from django.contrib.auth.models import User

from tastypie.test import ResourceTestCase, TestApiClient

from storybase_story.models import create_section, create_story, Section
from storybase_help.models import create_help

class HelpResourceTest(ResourceTestCase):
    def setUp(self):
        super(HelpResourceTest, self).setUp()
        # TODO: If we end up supporting the PATCH method, use our
        # FixedTestApiClient instead of the default
        self.api_client = TestApiClient()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 'test@example.com', self.password)

    def test_get_detail(self):
        help = create_help(title="Test Help Item",
                          body="Test Help Item body")
        uri = '/api/0.1/help/%s/' % (help.help_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(self.deserialize(resp)['title'],
                        "Test Help Item")
        self.assertEqual(self.deserialize(resp)['body'],
                        "Test Help Item body")

    def test_get_detail_by_slug(self):
        help = create_help(title="Test Help Item",
                          body="Test Help Item body",
                          slug="test")
        uri = '/api/0.1/help/%s/' % (help.slug)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(self.deserialize(resp)['title'],
                        "Test Help Item")
        self.assertEqual(self.deserialize(resp)['body'],
                        "Test Help Item body")

    def test_get_list_for_section(self):
        section_help = create_help(title="Test section help item",
                          body="Test section help item body")
        nonsection_help = create_help(title="Test non-section help item",
                          body="Test non-section help item body",
                          slug='test-nonsection')
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status="published",
                             language="en")
        section = create_section(title="Test Section 1", story=story,
                                 help=section_help)

        uri = '/api/0.1/help/sections/%s/' % (section.section_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        self.assertEqual(self.deserialize(resp)['objects'][0]['title'],
                        "Test section help item")
        self.assertEqual(self.deserialize(resp)['objects'][0]['body'],
                        "Test section help item body")

    def test_post_list_for_section(self):
        section_help = create_help(title="Test section help item",
                          body="Test section help item body")
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status="published",
                             language="en", author=self.user)
        section = create_section(title="Test Section 1", story=story)
        self.assertEqual(section.help, None)
        post_data = {
            'help_id': section_help.help_id
        }
        uri = '/api/0.1/help/sections/%s/' % (section.section_id)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        updated_section = Section.objects.get(pk=section.pk)
        self.assertEqual(updated_section.help, section_help)

    def test_post_list_for_section_unauthorized_unauthenticated(self):
        """
        Test that anonymous users cannot set the help item for a section
        """
        section_help = create_help(title="Test section help item",
                          body="Test section help item body")
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status="published",
                             language="en", author=self.user)
        section = create_section(title="Test Section 1", story=story)
        self.assertEqual(section.help, None)
        post_data = {
            'help_id': section_help.help_id
        }
        uri = '/api/0.1/help/sections/%s/' % (section.section_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpUnauthorized(resp)

    def test_post_list_for_section_unauthorized_other_user(self):
        """
        Test that a user can't set the help text for another user's section
        """
        user2 = User.objects.create(username="test2", 
            email="test2@example.com", password="test2")
        section_help = create_help(title="Test section help item",
                          body="Test section help item body")
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status="published",
                             language="en", author=user2)
        section = create_section(title="Test Section 1", story=story)
        self.assertEqual(section.help, None)
        post_data = {
            'help_id': section_help.help_id
        }
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/help/sections/%s/' % (section.section_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpUnauthorized(resp)
