# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Help.searchable'
        db.add_column('storybase_help_help', 'searchable', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Help.searchable'
        db.delete_column('storybase_help_help', 'searchable')


    models = {
        'storybase_help.help': {
            'Meta': {'object_name': 'Help'},
            'help_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'searchable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'storybase_help.helptranslation': {
            'Meta': {'object_name': 'HelpTranslation'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'help': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['storybase_help.Help']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'title': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        }
    }

    complete_apps = ['storybase_help']
