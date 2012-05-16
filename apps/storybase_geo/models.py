from django.contrib.gis.db import models

class DenverNeighborhood(models.Model):
    neigspss = models.CharField(max_length=8)
    name = models.CharField(max_length=25)
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    name_lc = models.CharField(max_length=50)
    neigh_id = models.IntegerField()
    acres = models.FloatField()
    sqm = models.FloatField()
    identifier = models.IntegerField()
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name_lc

# Auto-generated `LayerMapping` dictionary for DenverNeighborhood model
denverneighborhood_mapping = {
    'neigspss' : 'NEIGSPSS',
    'name' : 'NAME',
    'shape_leng' : 'Shape_Leng',
    'shape_area' : 'Shape_Area',
    'name_lc' : 'NAME_LC',
    'neigh_id' : 'NEIGH_ID',
    'acres' : 'Acres',
    'sqm' : 'SQM',
    'identifier' : 'Identifier',
    'geom' : 'MULTIPOLYGON',
}

class Corridor(models.Model):
    name = models.CharField(max_length=50, blank=True)
    objectid = models.IntegerField()
    perimeter = models.FloatField()
    area = models.FloatField()
    acres = models.FloatField()
    hectares = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

# Auto-generated `LayerMapping` dictionary for Corridor model
corridor_mapping = {
    'objectid' : 'OBJECTID',
    'perimeter' : 'Perimeter',
    'area' : 'Area',
    'acres' : 'Acres',
    'hectares' : 'Hectares',
    'geom' : 'MULTIPOLYGON',
}

class Hub(models.Model):
    grouped_name = models.CharField(max_length=50)
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.grouped_name

# Auto-generated `LayerMapping` dictionary for Hub model
hub_mapping = {
    'grouped_name' : 'GroupedNam',
    'geom' : 'MULTIPOLYGON',
}
