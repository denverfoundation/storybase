from tastypie.test import ResourceTestCase, TestApiClient

from storybase_help.models import create_help

class HelpResourceTest(ResourceTestCase):
    def setUp(self):
        super(HelpResourceTest, self).setUp()
        # TODO: If we end up supporting the PATCH method, use our
        # FixedTestApiClient instead of the default
        self.api_client = TestApiClient()

    def test_get_detail(self):
        obj = create_help(title="Test Help Item",
                          body="Test Help Item body")
        uri = '/api/0.1/help/%s/' % (obj.help_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(self.deserialize(resp)['title'],
                        "Test Help Item")
        self.assertEqual(self.deserialize(resp)['body'],
                        "Test Help Item body")

    def test_get_detail_by_slug(self):
        obj = create_help(title="Test Help Item",
                          body="Test Help Item body",
                          slug="test")
        uri = '/api/0.1/help/%s/' % (obj.slug)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(self.deserialize(resp)['title'],
                        "Test Help Item")
        self.assertEqual(self.deserialize(resp)['body'],
                        "Test Help Item body")
