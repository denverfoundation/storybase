# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DenverNeighborhood'
        db.create_table('storybase_place_denverneighborhood', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('neigspss', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('shape_leng', self.gf('django.db.models.fields.FloatField')()),
            ('shape_area', self.gf('django.db.models.fields.FloatField')()),
            ('name_lc', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('neigh_id', self.gf('django.db.models.fields.IntegerField')()),
            ('acres', self.gf('django.db.models.fields.FloatField')()),
            ('sqm', self.gf('django.db.models.fields.FloatField')()),
            ('identifier', self.gf('django.db.models.fields.IntegerField')()),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('storybase_place', ['DenverNeighborhood'])


    def backwards(self, orm):
        
        # Deleting model 'DenverNeighborhood'
        db.delete_table('storybase_place_denverneighborhood')


    models = {
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
        }
    }

    complete_apps = ['storybase_place']
