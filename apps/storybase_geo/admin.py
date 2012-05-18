from django.contrib.gis import admin
from mptt.admin import MPTTModelAdmin

from storybase.fields import ShortTextField
from storybase.widgets import AdminLongTextInputWidget
from storybase_geo.models import GeoLevel, Location, Place, PlaceRelation

class LocationAdmin(admin.OSMGeoAdmin):
    formfield_overrides = {
        ShortTextField: {'widget': AdminLongTextInputWidget},
    }
    list_filter = ['stories']


class PlaceRelationInline(admin.StackedInline):
    model = PlaceRelation
    fk_name = 'child'
    extra = 0


class PlaceAdmin(admin.OSMGeoAdmin):
    formfield_overrides = {
        ShortTextField: {'widget': AdminLongTextInputWidget},
    }
    inlines = (PlaceRelationInline,)
    list_display = ['name', 'geolevel']
    list_filter = ['geolevel']


admin.site.register(GeoLevel, MPTTModelAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Place, PlaceAdmin)
