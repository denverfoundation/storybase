from django.contrib.gis import admin
from mptt.admin import MPTTModelAdmin

from storybase.fields import ShortTextField
from storybase.widgets import AdminLongTextInputWidget
from storybase_geo.models import GeoLevel, Location

class LocationAdmin(admin.OSMGeoAdmin):
    formfield_overrides = {
        ShortTextField: {'widget': AdminLongTextInputWidget},
    }
    list_filter = ['stories']

admin.site.register(GeoLevel, MPTTModelAdmin)
admin.site.register(Location, LocationAdmin)
