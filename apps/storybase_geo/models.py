from django.contrib.gis.db import models
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from uuidfield.fields import UUIDField
from storybase.fields import ShortTextField

class Location(models.Model):
    """A location with a specific address or latitude and longitude"""
    location_id = UUIDField(auto=True)
    name = ShortTextField(blank=True)
    address = ShortTextField(blank=True)
    address2 = ShortTextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True,
                             choices=STATE_CHOICES)
    postcode = models.CharField(max_length=255, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    point = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        if self.name:
            unicode_rep = u"%s" % self.name
        elif self.address or self.city or self.state or self.postcode:
            unicode_rep = u", ".join([self.address, self.city, self.state])
	    unicode_rep = u" ".join([unicode_rep, self.postcode])
        else:
            return u"Location %s" % self.location_id

        return unicode_rep
