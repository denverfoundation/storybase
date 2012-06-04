from django.http import HttpRequest
from django.test import TestCase

from storybase_geo.api import GeocoderResource
from storybase_geo.models import Location

class LocationModelTest(TestCase):
    def test_geocode_on_save(self):
        """
        Tests that address information in a Location is geocoded when the
        Location is saved
        """
        loc = Location(name="The Piton Foundation",
                       address="370 17th St",
                       address2="#5300",
                       city="Denver",
                       state="CO",
                       postcode="80202")
        loc.save()
        self.assertEqual(loc.lat, 39.7438167)
        self.assertEqual(loc.lng, -104.9884953)
        self.assertEqual(loc.point.x, -104.9884953)
        self.assertEqual(loc.point.y, 39.7438167)

    def test_geocode_on_change(self):
        """
        Tests that address information in a Location is re-geocoded when
        the address is changed.
        """
        loc = Location(name="The Piton Foundation",
                       address="370 17th St",
                       address2="#5300",
                       city="Denver",
                       state="CO",
                       postcode="80202")
        loc.save()
        self.assertEqual(loc.lat, 39.7438167)
        self.assertEqual(loc.lng, -104.9884953)
        loc.name = "The Hull House"
        loc.address = "800 S. Halsted St."
        loc.city = "Chicago"
        loc.state = "IL"
        loc.postcode = "60607"
        loc.save()
        self.assertEqual(loc.lat, 41.8716782)
        self.assertEqual(loc.lng, -87.6474517)
        self.assertEqual(loc.point.x, -87.6474517)
        self.assertEqual(loc.point.y, 41.8716782)

class GeocoderResourceTest(TestCase):
    """Tests for geocoding endpoint"""
    def setUp(self):
        self._old_settings = {}

    def tearDown(self):
        from storybase_geo import settings as geo_settings
        for key, value in self._old_settings.items():
            setattr(geo_settings, key, value)

    def _select_yahoo_geocoder(self):
        from storybase_geo import settings as geo_settings
        self._old_settings['STORYBASE_GEOCODER'] = geo_settings.STORYBASE_GEOCODER
        self._old_settings['STORYBASE_GEOCODER_ARGS'] = geo_settings.STORYBASE_GEOCODER_ARGS
        geo_settings.STORYBASE_GEOCODER = "geopy.geocoders.Yahoo"
        geo_settings.STORYBASE_GEOCODER_ARGS = {
            'app_id': ""
        }

    def assertApxEqual(self, value1, value2, precision=1e-03):
        """Tests that values are approximately equal to each other"""
        if (not (abs(value1 - value2) <= precision)):
            self.fail("abs(%f - %f) is not less than %f" %
                      (value1, value2, precision))

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

