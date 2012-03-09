# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FilerImageAsset'
        db.create_table('storybase_asset_filerimageasset', (
            ('asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.Asset'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('storybase_asset', ['FilerImageAsset'])

        # Adding M2M table for field translations on 'FilerImageAsset'
        db.create_table('storybase_asset_filerimageasset_translations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filerimageasset', models.ForeignKey(orm['storybase_asset.filerimageasset'], null=False)),
            ('filerimageassettranslation', models.ForeignKey(orm['storybase_asset.filerimageassettranslation'], null=False))
        ))
        db.create_unique('storybase_asset_filerimageasset_translations', ['filerimageasset_id', 'filerimageassettranslation_id'])

        # Adding model 'ExternalAssetTranslation'
        db.create_table('storybase_asset_externalassettranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_asset_externalassettranslation_related', to=orm['storybase_asset.Asset'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('storybase_asset', ['ExternalAssetTranslation'])

        # Adding unique constraint on 'ExternalAssetTranslation', fields ['asset', 'language']
        db.create_unique('storybase_asset_externalassettranslation', ['asset_id', 'language'])

        # Adding model 'ExternalAsset'
        db.create_table('storybase_asset_externalasset', (
            ('asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.Asset'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('storybase_asset', ['ExternalAsset'])

        # Adding M2M table for field translations on 'ExternalAsset'
        db.create_table('storybase_asset_externalasset_translations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('externalasset', models.ForeignKey(orm['storybase_asset.externalasset'], null=False)),
            ('externalassettranslation', models.ForeignKey(orm['storybase_asset.externalassettranslation'], null=False))
        ))
        db.create_unique('storybase_asset_externalasset_translations', ['externalasset_id', 'externalassettranslation_id'])

        # Adding model 'FilerImageAssetTranslation'
        db.create_table('storybase_asset_filerimageassettranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_asset_filerimageassettranslation_related', to=orm['storybase_asset.Asset'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'])),
        ))
        db.send_create_signal('storybase_asset', ['FilerImageAssetTranslation'])

        # Adding unique constraint on 'FilerImageAssetTranslation', fields ['asset', 'language']
        db.create_unique('storybase_asset_filerimageassettranslation', ['asset_id', 'language'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'FilerImageAssetTranslation', fields ['asset', 'language']
        db.delete_unique('storybase_asset_filerimageassettranslation', ['asset_id', 'language'])

        # Removing unique constraint on 'ExternalAssetTranslation', fields ['asset', 'language']
        db.delete_unique('storybase_asset_externalassettranslation', ['asset_id', 'language'])

        # Deleting model 'FilerImageAsset'
        db.delete_table('storybase_asset_filerimageasset')

        # Removing M2M table for field translations on 'FilerImageAsset'
        db.delete_table('storybase_asset_filerimageasset_translations')

        # Deleting model 'ExternalAssetTranslation'
        db.delete_table('storybase_asset_externalassettranslation')

        # Deleting model 'ExternalAsset'
        db.delete_table('storybase_asset_externalasset')

        # Removing M2M table for field translations on 'ExternalAsset'
        db.delete_table('storybase_asset_externalasset_translations')

        # Deleting model 'FilerImageAssetTranslation'
        db.delete_table('storybase_asset_filerimageassettranslation')


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
        'filer.file': {
            'Meta': {'object_name': 'File'},
            '_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_file_type_plugin_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_files'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            'has_all_mandatory_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_files'", 'null': 'True', 'to': "orm['auth.User']"}),
            'sha1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.folder': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('parent', 'name'),)", 'object_name': 'Folder'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'filer_owned_folders'", 'null': 'True', 'to': "orm['auth.User']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['filer.Folder']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'filer.image': {
            'Meta': {'object_name': 'Image', '_ormbases': ['filer.File']},
            '_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            '_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_taken': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'default_alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'default_caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['filer.File']", 'unique': 'True', 'primary_key': 'True'}),
            'must_always_publish_author_credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'must_always_publish_copyright': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_location': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'storybase_asset.asset': {
            'Meta': {'object_name': 'Asset'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assets'", 'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'storybase_asset.externalasset': {
            'Meta': {'object_name': 'ExternalAsset', '_ormbases': ['storybase_asset.Asset']},
            'asset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.Asset']", 'unique': 'True', 'primary_key': 'True'}),
            'translations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['storybase_asset.ExternalAssetTranslation']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'storybase_asset.externalassettranslation': {
            'Meta': {'unique_together': "(('asset', 'language'),)", 'object_name': 'ExternalAssetTranslation'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_asset_externalassettranslation_related'", 'to': "orm['storybase_asset.Asset']"}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'storybase_asset.filerimageasset': {
            'Meta': {'object_name': 'FilerImageAsset', '_ormbases': ['storybase_asset.Asset']},
            'asset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.Asset']", 'unique': 'True', 'primary_key': 'True'}),
            'translations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['storybase_asset.FilerImageAssetTranslation']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'storybase_asset.filerimageassettranslation': {
            'Meta': {'unique_together': "(('asset', 'language'),)", 'object_name': 'FilerImageAssetTranslation'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_asset_filerimageassettranslation_related'", 'to': "orm['storybase_asset.Asset']"}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']"}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'storybase_asset.htmlasset': {
            'Meta': {'object_name': 'HtmlAsset', '_ormbases': ['storybase_asset.Asset']},
            'asset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.Asset']", 'unique': 'True', 'primary_key': 'True'}),
            'translations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['storybase_asset.HtmlAssetTranslation']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'storybase_asset.htmlassettranslation': {
            'Meta': {'unique_together': "(('asset', 'language'),)", 'object_name': 'HtmlAssetTranslation'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_asset_htmlassettranslation_related'", 'to': "orm['storybase_asset.Asset']"}),
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['storybase_asset']
