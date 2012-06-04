"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

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
        self.resource = GeocoderResource()


    def test_get_default_geocoder(self):
        """Test that the OpenMapQuest/Nominatum geocoder is used by default"""
        geocoder = self.resource.get_geocoder()
        self.assertEqual(geocoder.__class__.__name__,
                         "OpenMapQuest")

    def test_geocode_with_default_geocoder(self):
        """Test geocoding with default geocoder"""
        req = HttpRequest()
        req.method = 'GET'
        req.GET['q'] = "370 17th St, Denver"
        results = self.resource.obj_get_list(req)
        self.assertEqual(results[0].lat, 39.7434926) 
        self.assertEqual(results[0].lng, -104.9886368) 
