# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TagSet'
        db.create_table('storybase_tag_tagset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('storybase_tag', ['TagSet'])

        # Adding M2M table for field tags on 'TagSet'
        db.create_table('storybase_tag_tagset_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tagset', models.ForeignKey(orm['storybase_tag.tagset'], null=False)),
            ('tag', models.ForeignKey(orm['storybase_tag.tag'], null=False))
        ))
        db.create_unique('storybase_tag_tagset_tags', ['tagset_id', 'tag_id'])


    def backwards(self, orm):
        
        # Deleting model 'TagSet'
        db.delete_table('storybase_tag_tagset')

        # Removing M2M table for field tags on 'TagSet'
        db.delete_table('storybase_tag_tagset_tags')


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
        },
        'storybase_tag.tagset': {
            'Meta': {'object_name': 'TagSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tag_set'", 'symmetrical': 'False', 'to': "orm['storybase_tag.Tag']"})
        }
    }

    complete_apps = ['storybase_tag']
