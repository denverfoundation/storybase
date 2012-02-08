# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Asset'
        db.create_table('storybase_asset_asset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assets', to=orm['auth.User'])),
        ))
        db.send_create_signal('storybase_asset', ['Asset'])

        # Deleting field 'ExternalAsset.title'
        db.delete_column('storybase_asset_externalasset', 'title')

        # Deleting field 'ExternalAsset.caption'
        db.delete_column('storybase_asset_externalasset', 'caption')

        # Deleting field 'ExternalAsset.user'
        db.delete_column('storybase_asset_externalasset', 'user_id')

        # Deleting field 'ExternalAsset.type'
        db.delete_column('storybase_asset_externalasset', 'type')

        # Deleting field 'ExternalAsset.id'
        db.delete_column('storybase_asset_externalasset', 'id')

        # Adding field 'ExternalAsset.asset_ptr'
        db.add_column('storybase_asset_externalasset', 'asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(default=1, to=orm['storybase_asset.Asset'], unique=True, primary_key=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'Asset'
        db.delete_table('storybase_asset_asset')

        # User chose to not deal with backwards NULL issues for 'ExternalAsset.title'
        raise RuntimeError("Cannot reverse this migration. 'ExternalAsset.title' and its values cannot be restored.")

        # Adding field 'ExternalAsset.caption'
        db.add_column('storybase_asset_externalasset', 'caption', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'ExternalAsset.user'
        raise RuntimeError("Cannot reverse this migration. 'ExternalAsset.user' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ExternalAsset.type'
        raise RuntimeError("Cannot reverse this migration. 'ExternalAsset.type' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ExternalAsset.id'
        raise RuntimeError("Cannot reverse this migration. 'ExternalAsset.id' and its values cannot be restored.")

        # Deleting field 'ExternalAsset.asset_ptr'
        db.delete_column('storybase_asset_externalasset', 'asset_ptr_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'storybase_asset.asset': {
            'Meta': {'object_name': 'Asset'},
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assets'", 'to': "orm['auth.User']"})
        },
        'storybase_asset.externalasset': {
            'Meta': {'object_name': 'ExternalAsset', '_ormbases': ['storybase_asset.Asset']},
            'asset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.Asset']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['storybase_asset']
