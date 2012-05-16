from django.contrib.gis import admin
from storybase_geo.models import Location

admin.site.register(Location, admin.OSMGeoAdmin)
