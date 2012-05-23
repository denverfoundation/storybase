# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GeoLevel'
        db.create_table('storybase_geo_geolevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['storybase_geo.GeoLevel'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('storybase_geo', ['GeoLevel'])

        # Adding model 'Location'
        db.create_table('storybase_geo_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('name', self.gf('storybase.fields.ShortTextField')(blank=True)),
            ('address', self.gf('storybase.fields.ShortTextField')(blank=True)),
            ('address2', self.gf('storybase.fields.ShortTextField')(blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lng', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('point', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
        ))
        db.send_create_signal('storybase_geo', ['Location'])

        # Adding model 'Place'
        db.create_table('storybase_geo_place', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('storybase.fields.ShortTextField')()),
            ('geolevel', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='places', null=True, to=orm['storybase_geo.GeoLevel'])),
            ('boundary', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(null=True, blank=True)),
            ('place_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
        ))
        db.send_create_signal('storybase_geo', ['Place'])

        # Adding model 'PlaceRelation'
        db.create_table('storybase_geo_placerelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='place_child', to=orm['storybase_geo.Place'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='place_parent', to=orm['storybase_geo.Place'])),
        ))
        db.send_create_signal('storybase_geo', ['PlaceRelation'])

        # Adding unique constraint on 'PlaceRelation', fields ['parent', 'child']
        db.create_unique('storybase_geo_placerelation', ['parent_id', 'child_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'PlaceRelation', fields ['parent', 'child']
        db.delete_unique('storybase_geo_placerelation', ['parent_id', 'child_id'])

        # Deleting model 'GeoLevel'
        db.delete_table('storybase_geo_geolevel')

        # Deleting model 'Location'
        db.delete_table('storybase_geo_location')

        # Deleting model 'Place'
        db.delete_table('storybase_geo_place')

        # Deleting model 'PlaceRelation'
        db.delete_table('storybase_geo_placerelation')


    models = {
        'storybase_geo.geolevel': {
            'Meta': {'object_name': 'GeoLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['storybase_geo.GeoLevel']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'storybase_geo.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'address2': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'location_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'name': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'storybase_geo.place': {
            'Meta': {'object_name': 'Place'},
            'boundary': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['storybase_geo.Place']", 'null': 'True', 'through': "orm['storybase_geo.PlaceRelation']", 'blank': 'True'}),
            'geolevel': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'places'", 'null': 'True', 'to': "orm['storybase_geo.GeoLevel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('storybase.fields.ShortTextField', [], {}),
            'place_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        'storybase_geo.placerelation': {
            'Meta': {'unique_together': "(('parent', 'child'),)", 'object_name': 'PlaceRelation'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'place_parent'", 'to': "orm['storybase_geo.Place']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'place_child'", 'to': "orm['storybase_geo.Place']"})
        }
    }

    complete_apps = ['storybase_geo']
