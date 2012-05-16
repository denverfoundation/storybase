from django.contrib.gis import admin
from storybase.fields import ShortTextField
from storybase.widgets import AdminLongTextInputWidget
from storybase_geo.models import Location

class LocationAdmin(admin.OSMGeoAdmin):
    formfield_overrides = {
        ShortTextField: {'widget': AdminLongTextInputWidget},
    }

admin.site.register(Location, LocationAdmin)
