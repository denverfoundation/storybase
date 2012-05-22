from django import forms
from django.forms import widgets
from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from mptt.admin import MPTTModelAdmin

from storybase.admin import Select2StackedInline
from storybase.fields import ShortTextField
from storybase.widgets import AdminLongTextInputWidget, Select2Select
from storybase_geo.models import GeoLevel, Location, Place, PlaceRelation

class LocationAdmin(admin.OSMGeoAdmin):
    formfield_overrides = {
        ShortTextField: {'widget': AdminLongTextInputWidget},
    }
    list_filter = ['stories']


class PlaceRelationAdminForm(forms.ModelForm):
    """
    Custom form class for PlaceRelation models

    This form class limits the parent field queryset to a particular
    geolevel and provides AJAX autocomplete using the Select2 widget
    (as there will likely be many items)

    """
    parent = forms.models.ModelChoiceField(queryset=Place.objects.all(),
                                           to_field_name='place_id',
                                           widget=Select2Select)

    def __init__(self, *args, **kwargs):
        super(PlaceRelationAdminForm, self).__init__(*args, **kwargs)
        # We're using a public API endpoint that hides the "real" pks
        # and instead exposes a UUID-based key.  We need to translate
        # between the UUID and the Django pk
        parent_pk = self.initial.get('parent', None)
        if parent_pk:
            parent_obj = Place.objects.get(pk=parent_pk)
            self.initial['parent'] = parent_obj.place_id
            
        if (hasattr(self.instance, 'child') and
                self.instance.child.geolevel):
            # This is a bound instance
            # Limit the queryset
            self.fields['parent'].queryset = Place.objects.filter(
                geolevel=self.instance.child.geolevel.parent)
            widget_style = self.fields['parent'].widget.attrs.get(
                'style', None)
            addl_styles = 'min-width: 200px;'
            widget_style = ("%s %s" % (widget_style, addl_styles)
                            if widget_style else addl_styles)
            self.fields['parent'].widget.attrs['style'] = widget_style

        else:
            # This is a new instance
            # Swap the selection widget out with a hidden input
            # (as required by Select2) and pass some parameters to
            # client-side JavaScript
            attrs = {
              'class': 'select2-enable',
              'data-ajax-url': reverse("api_dispatch_list", kwargs={
                  'resource_name': 'places', 'api_name': '0.1'
               }),
              'data-ajax-datatype': 'json',
              'data-ajax-result-attr': 'name',
              'data-ajax-selection-attr': 'name',
              'data-ajax-filter-function': 'geoLevelFilters',
              'style': 'min-width: 200px;'
            }
            self.fields['parent'].widget = widgets.HiddenInput(attrs=attrs)


class PlaceRelationInline(Select2StackedInline):
    model = PlaceRelation
    form = PlaceRelationAdminForm
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
