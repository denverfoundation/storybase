# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'OfficialTag'
        db.delete_table('storybase_tag_officialtag')

        # Deleting model 'OfficialTaggedItem'
        db.delete_table('storybase_tag_officialtaggeditem')

        # Adding model 'TaggedItem'
        db.create_table('storybase_tag_taggeditem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_tag_taggeditem_tagged_items', to=orm['contenttypes.ContentType'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_tag_taggeditem_items', to=orm['storybase_tag.Tag'])),
        ))
        db.send_create_signal('storybase_tag', ['TaggedItem'])

        # Adding model 'Tag'
        db.create_table('storybase_tag_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('official', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('storybase_tag', ['Tag'])


    def backwards(self, orm):
        
        # Adding model 'OfficialTag'
        db.create_table('storybase_tag_officialtag', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, unique=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('official', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('storybase_tag', ['OfficialTag'])

        # Adding model 'OfficialTaggedItem'
        db.create_table('storybase_tag_officialtaggeditem', (
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['storybase_tag.OfficialTag'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_tag_officialtaggeditem_tagged_items', to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal('storybase_tag', ['OfficialTaggedItem'])

        # Deleting model 'TaggedItem'
        db.delete_table('storybase_tag_taggeditem')

        # Deleting model 'Tag'
        db.delete_table('storybase_tag_tag')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'storybase_tag.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'storybase_tag.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_tag_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_tag_taggeditem_items'", 'to': "orm['storybase_tag.Tag']"})
        }
    }

    complete_apps = ['storybase_tag']
