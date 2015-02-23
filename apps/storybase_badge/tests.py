
from tastypie.test import ResourceTestCase


class BadgeResourceTest(ResourceTestCase):

    fixtures = ['denver_badges.json']

    def test_get_list_of_badges(self):

        response = self.api_client.get('/api/0.1/badges/', format='json')
        self.assertValidJSONResponse(response)

        objects = self.deserialize(response)['objects']

        self.assertEquals(objects[0], {
            u'description': u'Stories promoted by the Denver Foundation Staff.',
            u'icon_uri': '/static/img/badges/denver-foundation.png',
            u'id': 1,
            u'name': u'Denver Foundation',
            u'resource_uri': '/api/0.1/badges/1/'
        })
