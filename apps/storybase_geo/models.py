from geopy.geocoders.base import GeocoderError

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.db.models.signals import pre_save
from django.utils.translation import ugettext as _
from django_dag.models import edge_factory, node_factory
from mptt.models import MPTTModel, TreeForeignKey
from uuidfield.fields import UUIDField

from storybase.models import DirtyFieldsMixin, PermissionMixin
from storybase.fields import ShortTextField
from storybase_geo.utils import get_geocoder

class GeoLevel(MPTTModel):
    """A hierarchical type of geography"""
    name = models.CharField(_("Name"), max_length=255, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, 
                            related_name='children',
                            verbose_name=_("Parent"))
    slug = models.SlugField(_("Slug"), unique=True)

    def __unicode__(self):
        return self.name


class LocationPermission(PermissionMixin):
    """Permissions for the Story model"""
    def user_can_change(self, user):
        from storybase_user.utils import is_admin

        if not user.is_active:
            return False

        if self.owner == user:
            return True

        if is_admin(user):
            return True

        return False

    def user_can_add(self, user):
        if user.is_active:
            return True

        return False

    def user_can_delete(self, user):
        return self.user_can_change(user)


class Location(LocationPermission, DirtyFieldsMixin, models.Model):
    """A location with a specific address or latitude and longitude"""
    location_id = UUIDField(auto=True, verbose_name=_("Location ID"))
    name = ShortTextField(_("Name"), blank=True)
    address = ShortTextField(_("Address"), blank=True)
    address2 = ShortTextField(_("Address 2"), blank=True)
    city = models.CharField(_("City"), max_length=255, blank=True)
    state = models.CharField(_("State"), max_length=255, blank=True,
                             choices=STATE_CHOICES)
    postcode = models.CharField(_("Postal Code"), max_length=255, blank=True)
    lat = models.FloatField(_("Latitude"), blank=True, null=True)
    lng = models.FloatField(_("Longitude"), blank=True, null=True)
    point = models.PointField(_("Point"), blank=True, null=True)
    owner = models.ForeignKey(User, related_name="locations", blank=True,
                              null=True)
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

    def _geocode(self, address):
        point = None
        geocoder = get_geocoder()
        # There might be more than one matching location.  For now, just
        # assume the first one.
        results = list(geocoder.geocode(address, exactly_one=False))
        if results:
            place, (lat, lng) = results[0]
            point = (lat, lng)

        return point


def geocode(sender, instance, **kwargs):
    """Geocode a Location instance based on its address fields"""
    changed_fields = instance.get_dirty_fields().keys()
    if ('lat' in changed_fields or 'lng' in changed_fields or
          (instance.lat is not None and instance.lng is not None and
           instance.point is None)):
        # A latitude or longitude was explictly set or changed
        # Set or update the point
        instance.point = Point(instance.lng, instance.lat)
    elif ('address' in changed_fields or 'city' in changed_fields or
            'state' in changed_fields or 'postcode' in changed_fields or
            instance.lat is None or instance.lng is None):
        point = instance._geocode("%s %s %s %s" % 
            (instance.address, instance.city, instance.state, 
             instance.postcode))
        if point:
            (lat, lng) = point
            instance.lat = lat
            instance.lng = lng
            instance.point = Point(lng, lat)


pre_save.connect(geocode, sender=Location)


class Place(node_factory('PlaceRelation')):
    """
    A larger scale geographic area such as a neighborhood or zip code
    
    Places are related hierachically using a directed graph as a place can
    have multiple parents.

    """
    name = ShortTextField(_("Name"))
    geolevel = models.ForeignKey(GeoLevel, null=True, blank=True,  
                                 related_name='places',
                                 verbose_name=_("GeoLevel"))
    boundary = models.MultiPolygonField(blank=True, null=True,
                                        verbose_name=_("Boundary"))
    place_id = UUIDField(auto=True, verbose_name=_("Place ID"))

    def __unicode__(self):
        return self.name


class PlaceRelation(edge_factory(Place, concrete=False)):
    class Meta:
        unique_together = (("parent", "child"),)
