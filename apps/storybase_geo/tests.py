from django.http import HttpRequest
from django.contrib.auth.models import User

from tastypie.test import ResourceTestCase, TestApiClient

from storybase.tests.base import (SettingsChangingTestCase,
                                  SloppyComparisonTestMixin)
from storybase_geo.api import GeocoderResource
from storybase_geo.models import Location
from storybase_story.models import create_story

class YahooGeocoderTestMixin(object):
    """Mixin that sets gecoder to Yahoo

    Must be used with SettingsChangingTestCase

    """
    def _select_yahoo_geocoder(self):
        settings = self.get_settings_module()
        self._old_settings['STORYBASE_GEOCODER'] = getattr(settings, 'STORYBASE_GEOCODER', None)
        self._old_settings['STORYBASE_GEOCODER_ARGS'] = getattr(settings, 'STORYBASE_GEOCODER_ARGS', None)
        self.set_setting('STORYBASE_GEOCODER', "geopy.geocoders.Yahoo")
        self.set_setting('STORYBASE_GEOCODER_ARGS', {
            'app_id': ""
        })


class LocationModelTest(YahooGeocoderTestMixin, SloppyComparisonTestMixin, 
        SettingsChangingTestCase):
    def get_settings_module(self):
        from storybase_geo import settings
        return settings

    def test_geocode(self):
        """Test internal geocoding method"""
        self._select_yahoo_geocoder()
        loc = Location()
        latlng = loc._geocode("370 17th St Denver CO 80202")
        self.assertApxEqual(latlng[0], 39.7438167)
        self.assertApxEqual(latlng[1], -104.9884953)

    def test_geocode_on_save(self):
        """
        Tests that address information in a Location is geocoded when the
        Location is saved
        """
        self._select_yahoo_geocoder()
        loc = Location(name="The Piton Foundation",
                       address="370 17th St",
                       address2="#5300",
                       city="Denver",
                       state="CO",
                       postcode="80202")
        loc.save()
        self.assertApxEqual(loc.lat, 39.7438167)
        self.assertApxEqual(loc.lng, -104.9884953)
        self.assertApxEqual(loc.point.x, -104.9884953)
        self.assertApxEqual(loc.point.y, 39.7438167)

    def test_geocode_on_change(self):
        """
        Tests that address information in a Location is re-geocoded when
        the address is changed.
        """
        self._select_yahoo_geocoder()
        loc = Location(name="The Piton Foundation",
                       address="370 17th St",
                       address2="#5300",
                       city="Denver",
                       state="CO",
                       postcode="80202")
        loc.save()
        self.assertApxEqual(loc.lat, 39.7438167)
        self.assertApxEqual(loc.lng, -104.9884953)
        loc.name = "The Hull House"
        loc.address = "800 S. Halsted St."
        loc.city = "Chicago"
        loc.state = "IL"
        loc.postcode = "60607"
        loc.save()
        self.assertApxEqual(loc.lat, 41.8716782)
        self.assertApxEqual(loc.lng, -87.6474517)
        self.assertApxEqual(loc.point.x, -87.6474517)
        self.assertApxEqual(loc.point.y, 41.8716782)


class GeocoderResourceTest(YahooGeocoderTestMixin, SloppyComparisonTestMixin,
        SettingsChangingTestCase):
    """Tests for geocoding endpoint"""
    def get_settings_module(self):
        from storybase_geo import settings
        return settings

    def test_get_default_geocoder(self):
        """Test that the OpenMapQuest/Nominatum geocoder is used by default"""
        resource = GeocoderResource()
        geocoder = resource.get_geocoder()
        self.assertEqual(geocoder.__class__.__name__,
                         "OpenMapQuest")

    def test_geocode_with_default_geocoder(self):
        """Test geocoding with default geocoder"""
        resource = GeocoderResource()
        req = HttpRequest()
        req.method = 'GET'
        req.GET['q'] = "370 17th St, Denver"
        results = resource.obj_get_list(req)
        self.assertEqual(results[0].lat, 39.7434926) 
        self.assertEqual(results[0].lng, -104.9886368) 

    def test_get_yahoo_geocoder(self):
        """Test that Yahoo geocoder can replace default""" 
        self._select_yahoo_geocoder()
        resource = GeocoderResource()
        geocoder = resource.get_geocoder()
        self.assertEqual(geocoder.__class__.__name__,
                         "Yahoo")

    def test_geocode_address_yahoo(self):
        """Test geocoding a street address with Yahoo geocoder"""
        self._select_yahoo_geocoder()
        resource = GeocoderResource()
        req = HttpRequest()
        req.method = 'GET'
        req.GET['q'] = "370 17th St, Denver, CO 80202"
        results = resource.obj_get_list(req)
        self.assertApxEqual(results[0].lat, 39.7434926) 
        self.assertApxEqual(results[0].lng, -104.9886368) 

    def test_geocode_intersection_yahoo(self):
        """Test geocoding an intersection with Yahoo geocoder"""
        self._select_yahoo_geocoder()
        resource = GeocoderResource()
        req = HttpRequest()
        req.method = 'GET'
        req.GET['q'] = "colfax and chambers, aurora, co"
        results = resource.obj_get_list(req)
        self.assertApxEqual(results[0].lat, 39.7399986) 
        self.assertApxEqual(results[0].lng, -104.8099387) 

    def test_geocode_city_state_yahoo(self):
        """Test geocoding a city and state with Yahoo geocoder"""
        self._select_yahoo_geocoder()
        resource = GeocoderResource()
        req = HttpRequest()
        req.method = 'GET'
        req.GET['q'] = "golden, co"
        results = resource.obj_get_list(req)
        self.assertApxEqual(results[0].lat, 39.756655, .001) 
        self.assertApxEqual(results[0].lng, -105.224949, .001) 

    def test_geocode_zip_yahoo(self):
        """Test geocoding a zip code with Yahoo geocoder"""
        self._select_yahoo_geocoder()
        resource = GeocoderResource()
        req = HttpRequest()
        req.method = 'GET'
        req.GET['q'] = "80202"
        results = resource.obj_get_list(req)
        self.assertApxEqual(results[0].lat, 39.7541032, .01)
        self.assertApxEqual(results[0].lng, -105.000224, .01) 

    def test_geocode_city_yahoo(self):
        """Test geocoding a city with Yahoo geocoder"""
        self._select_yahoo_geocoder()
        resource = GeocoderResource()
        req = HttpRequest()
        req.method = 'GET'
        req.GET['q'] = "Denver"
        results = resource.obj_get_list(req)
        self.assertApxEqual(results[0].lat, 39.737567, .01)
        self.assertApxEqual(results[0].lng, -104.9847179, .01)

    def test_geocode_failure_yahoo(self):
        """Test that results list is empty if no match is found"""
        self._select_yahoo_geocoder()
        resource = GeocoderResource()
        req = HttpRequest()
        req.method = 'GET'
        req.GET['q'] = "11zzzzzzzzzz1234asfdasdasgw"
        results = resource.obj_get_list(req)
        self.assertEqual(len(results), 0)


class LocationResourceTest(ResourceTestCase):
    def setUp(self):
        super(LocationResourceTest, self).setUp()
        self.ap_client = TestApiClient()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 
            'test@example.com', self.password)
        self.user2 = User.objects.create_user("test2", "test2@example.com",
                                              "test2")
        self.story = create_story(title="Test Story", summary="Test Summary",
            byline="Test Byline", status="published", language="en", 
            author=self.user)
        self.location_attrs = [
            {
                "name": "The Piton Foundation",
                "address": "370 17th St",
                "address2": "#5300",
                "city": "Denver",
                "state": "CO",
                "postcode": "80202",
            },
            {
                'name': "The Hull House",
                'address': "800 S. Halsted St.",
                "city": "Chicago",
                "state": "IL",
                "postcode": "60607",
            },
            {
                'name': "Bucktown-Wicker Park Library",
                'address': "1701 North Milwaukee Ave.",
                'city': "Chicago",
                'state': "IL",
                'postcode': "60647",
            }
        ]

    def test_get_list_with_story(self):
        for attrs in self.location_attrs:
            Location.objects.create(**attrs)
        self.assertEqual(Location.objects.count(), 3)
        self.story.locations.add(*list(Location.objects.filter(name__in=("The Hull House", "The Piton Foundation"))))
        self.story.save()
        self.assertEqual(self.story.locations.count(), 2)
        uri = '/api/0.1/locations/stories/%s/' % (self.story.story_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        for retrieved_attrs in self.deserialize(resp)['objects']:
            self.assertIn(retrieved_attrs['name'], ("The Hull House", "The Piton Foundation"))

    def test_post_list_with_story(self):
        post_data = {
            'name': "Mo Betta Green Market",
            'lat': 39.7533324751841,
            'lng': -104.979961178185
        }
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(self.story.locations.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/locations/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        returned_id = resp['location'].split('/')[-2]
        # Confirm that a location object was created
        self.assertEqual(Location.objects.count(), 1)
        # Compare the response data with the post_data
        self.assertEqual(self.deserialize(resp)['name'],
                         post_data['name'])
        self.assertEqual(self.deserialize(resp)['lat'],
                         post_data['lat'])
        self.assertEqual(self.deserialize(resp)['lng'],
                         post_data['lng'])
        created_obj = Location.objects.get()
        # Compare the id from the resource URI with the created object
        self.assertEqual(created_obj.location_id, returned_id)
        # Compare the created model instance with the post data
        self.assertEqual(created_obj.name, post_data['name'])
        self.assertEqual(created_obj.lat, post_data['lat'])
        self.assertEqual(created_obj.lng, post_data['lng'])
        # Test that the created object is associated with the story
        self.assertEqual(self.story.locations.count(), 1)
        self.assertIn(created_obj, self.story.locations.all())

    def test_post_list_with_story_unauthenticated(self):
        """Test that an unauthenticated user can't create a location"""
        post_data = {
            'name': "Mo Betta Green Market",
            'lat': 39.7533324751841,
            'lng': -104.979961178185
        }
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(self.story.locations.count(), 0)
        uri = '/api/0.1/locations/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpUnauthorized(resp)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(self.story.locations.count(), 0)

    def test_post_list_with_story_unauthorized(self):
        """
        Test that an authenticated user can't create a location
        associated with another user's story
        """
        self.story.author = self.user2
        self.story.save()
        post_data = {
            'name': "Mo Betta Green Market",
            'lat': 39.7533324751841,
            'lng': -104.979961178185
        }
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(self.story.locations.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/locations/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpUnauthorized(resp)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(self.story.locations.count(), 0)

    def test_delete_detail(self):
        obj = Location.objects.create(**self.location_attrs[0])
        obj.owner = self.user
        obj.save()
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(self.user.locations.count(), 1)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/locations/%s/' % (obj.location_id)
        resp = self.api_client.delete(uri, format='json')
        self.assertHttpAccepted(resp)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(self.user.locations.count(), 0)

    def test_delete_detail_unauthenticated(self):
        """Tests that an unauthenticated user cannot delete a location"""
        obj = Location.objects.create(**self.location_attrs[0])
        obj.owner = self.user
        obj.save()
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(self.user.locations.count(), 1)
        uri = '/api/0.1/locations/%s/' % (obj.location_id)
        resp = self.api_client.delete(uri, format='json')
        self.assertHttpUnauthorized(resp)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(self.user.locations.count(), 1)

    def test_delete_detail_unauthorized(self):
        """Tests that an unauthorized user cannot delete a location"""
        obj = Location.objects.create(**self.location_attrs[0])
        obj.owner = self.user2
        obj.save()
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(self.user2.locations.count(), 1)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/locations/%s/' % (obj.location_id)
        resp = self.api_client.delete(uri, format='json')
        self.assertHttpUnauthorized(resp)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(self.user2.locations.count(), 1)
