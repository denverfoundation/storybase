# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Hub'
        db.create_table('storybase_place_hub', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('grouped_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('storybase_place', ['Hub'])


    def backwards(self, orm):
        
        # Deleting model 'Hub'
        db.delete_table('storybase_place_hub')


    models = {
        'storybase_place.corridor': {
            'Meta': {'object_name': 'Corridor'},
            'acres': ('django.db.models.fields.FloatField', [], {}),
            'area': ('django.db.models.fields.FloatField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'hectares': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'objectid': ('django.db.models.fields.IntegerField', [], {}),
            'perimeter': ('django.db.models.fields.FloatField', [], {})
        },
        'storybase_place.denverneighborhood': {
            'Meta': {'object_name': 'DenverNeighborhood'},
            'acres': ('django.db.models.fields.FloatField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'name_lc': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'neigh_id': ('django.db.models.fields.IntegerField', [], {}),
            'neigspss': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'shape_area': ('django.db.models.fields.FloatField', [], {}),
            'shape_leng': ('django.db.models.fields.FloatField', [], {}),
            'sqm': ('django.db.models.fields.FloatField', [], {})
        },
        'storybase_place.hub': {
            'Meta': {'object_name': 'Hub'},
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'grouped_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['storybase_place']
