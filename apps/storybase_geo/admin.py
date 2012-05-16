from django.contrib.gis import admin
from models import Corridor, DenverNeighborhood, Hub

admin.site.register(Corridor, admin.OSMGeoAdmin)
admin.site.register(DenverNeighborhood, admin.OSMGeoAdmin)
admin.site.register(Hub, admin.OSMGeoAdmin)
