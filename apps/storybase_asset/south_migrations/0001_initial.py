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
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default=u'draft', max_length=10)),
            ('published', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('license', self.gf('django.db.models.fields.CharField')(default='CC BY-NC-SA', max_length=25)),
            ('asset_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('attribution', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assets', null=True, to=orm['auth.User'])),
            ('section_specific', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('asset_created', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('storybase_asset', ['Asset'])

        # Adding M2M table for field datasets on 'Asset'
        db.create_table('storybase_asset_asset_datasets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('asset', models.ForeignKey(orm['storybase_asset.asset'], null=False)),
            ('dataset', models.ForeignKey(orm['storybase_asset.dataset'], null=False))
        ))
        db.create_unique('storybase_asset_asset_datasets', ['asset_id', 'dataset_id'])

        # Adding model 'ExternalAsset'
        db.create_table('storybase_asset_externalasset', (
            ('asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.Asset'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('storybase_asset', ['ExternalAsset'])

        # Adding model 'ExternalAssetTranslation'
        db.create_table('storybase_asset_externalassettranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en', max_length=15)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_asset_externalassettranslation_related', to=orm['storybase_asset.Asset'])),
            ('title', self.gf('storybase.fields.ShortTextField')(blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('storybase_asset', ['ExternalAssetTranslation'])

        # Adding unique constraint on 'ExternalAssetTranslation', fields ['asset', 'language']
        db.create_unique('storybase_asset_externalassettranslation', ['asset_id', 'language'])

        # Adding model 'HtmlAsset'
        db.create_table('storybase_asset_htmlasset', (
            ('asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.Asset'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('storybase_asset', ['HtmlAsset'])

        # Adding model 'HtmlAssetTranslation'
        db.create_table('storybase_asset_htmlassettranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en', max_length=15)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_asset_htmlassettranslation_related', to=orm['storybase_asset.Asset'])),
            ('title', self.gf('storybase.fields.ShortTextField')(blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('storybase_asset', ['HtmlAssetTranslation'])

        # Adding unique constraint on 'HtmlAssetTranslation', fields ['asset', 'language']
        db.create_unique('storybase_asset_htmlassettranslation', ['asset_id', 'language'])

        # Adding model 'LocalImageAsset'
        db.create_table('storybase_asset_localimageasset', (
            ('asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.Asset'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('storybase_asset', ['LocalImageAsset'])

        # Adding model 'LocalImageAssetTranslation'
        db.create_table('storybase_asset_localimageassettranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en', max_length=15)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_asset_localimageassettranslation_related', to=orm['storybase_asset.Asset'])),
            ('title', self.gf('storybase.fields.ShortTextField')(blank=True)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'])),
        ))
        db.send_create_signal('storybase_asset', ['LocalImageAssetTranslation'])

        # Adding unique constraint on 'LocalImageAssetTranslation', fields ['asset', 'language']
        db.create_unique('storybase_asset_localimageassettranslation', ['asset_id', 'language'])

        # Adding model 'DataSet'
        db.create_table('storybase_asset_dataset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default=u'draft', max_length=10)),
            ('published', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('dataset_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('source', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('attribution', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='datasets', null=True, to=orm['auth.User'])),
            ('dataset_created', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('storybase_asset', ['DataSet'])

        # Adding model 'DataSetTranslation'
        db.create_table('storybase_asset_datasettranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation_id', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en', max_length=15)),
            ('dataset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_asset_datasettranslation_related', to=orm['storybase_asset.DataSet'])),
            ('title', self.gf('storybase.fields.ShortTextField')()),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('storybase_asset', ['DataSetTranslation'])

        # Adding unique constraint on 'DataSetTranslation', fields ['dataset', 'language']
        db.create_unique('storybase_asset_datasettranslation', ['dataset_id', 'language'])

        # Adding model 'ExternalDataSet'
        db.create_table('storybase_asset_externaldataset', (
            ('dataset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.DataSet'], unique=True, primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('storybase_asset', ['ExternalDataSet'])

        # Adding model 'LocalDataSet'
        db.create_table('storybase_asset_localdataset', (
            ('dataset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.DataSet'], unique=True, primary_key=True)),
            ('file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.File'])),
        ))
        db.send_create_signal('storybase_asset', ['LocalDataSet'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'DataSetTranslation', fields ['dataset', 'language']
        db.delete_unique('storybase_asset_datasettranslation', ['dataset_id', 'language'])

        # Removing unique constraint on 'LocalImageAssetTranslation', fields ['asset', 'language']
        db.delete_unique('storybase_asset_localimageassettranslation', ['asset_id', 'language'])

        # Removing unique constraint on 'HtmlAssetTranslation', fields ['asset', 'language']
        db.delete_unique('storybase_asset_htmlassettranslation', ['asset_id', 'language'])

        # Removing unique constraint on 'ExternalAssetTranslation', fields ['asset', 'language']
        db.delete_unique('storybase_asset_externalassettranslation', ['asset_id', 'language'])

        # Deleting model 'Asset'
        db.delete_table('storybase_asset_asset')

        # Removing M2M table for field datasets on 'Asset'
        db.delete_table('storybase_asset_asset_datasets')

        # Deleting model 'ExternalAsset'
        db.delete_table('storybase_asset_externalasset')

        # Deleting model 'ExternalAssetTranslation'
        db.delete_table('storybase_asset_externalassettranslation')

        # Deleting model 'HtmlAsset'
        db.delete_table('storybase_asset_htmlasset')

        # Deleting model 'HtmlAssetTranslation'
        db.delete_table('storybase_asset_htmlassettranslation')

        # Deleting model 'LocalImageAsset'
        db.delete_table('storybase_asset_localimageasset')

        # Deleting model 'LocalImageAssetTranslation'
        db.delete_table('storybase_asset_localimageassettranslation')

        # Deleting model 'DataSet'
        db.delete_table('storybase_asset_dataset')

        # Deleting model 'DataSetTranslation'
        db.delete_table('storybase_asset_datasettranslation')

        # Deleting model 'ExternalDataSet'
        db.delete_table('storybase_asset_externaldataset')

        # Deleting model 'LocalDataSet'
        db.delete_table('storybase_asset_localdataset')


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
            'asset_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'asset_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'attribution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'datasets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'assets'", 'blank': 'True', 'to': "orm['storybase_asset.DataSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'default': "'CC BY-NC-SA'", 'max_length': '25'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assets'", 'null': 'True', 'to': "orm['auth.User']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'section_specific': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'draft'", 'max_length': '10'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'storybase_asset.dataset': {
            'Meta': {'object_name': 'DataSet'},
            'attribution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dataset_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dataset_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'datasets'", 'null': 'True', 'to': "orm['auth.User']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'draft'", 'max_length': '10'})
        },
        'storybase_asset.datasettranslation': {
            'Meta': {'unique_together': "(('dataset', 'language'),)", 'object_name': 'DataSetTranslation'},
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_asset_datasettranslation_related'", 'to': "orm['storybase_asset.DataSet']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'title': ('storybase.fields.ShortTextField', [], {}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        'storybase_asset.externalasset': {
            'Meta': {'object_name': 'ExternalAsset', '_ormbases': ['storybase_asset.Asset']},
            'asset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.Asset']", 'unique': 'True', 'primary_key': 'True'})
        },
        'storybase_asset.externalassettranslation': {
            'Meta': {'unique_together': "(('asset', 'language'),)", 'object_name': 'ExternalAssetTranslation'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_asset_externalassettranslation_related'", 'to': "orm['storybase_asset.Asset']"}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'title': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'storybase_asset.externaldataset': {
            'Meta': {'object_name': 'ExternalDataSet', '_ormbases': ['storybase_asset.DataSet']},
            'dataset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.DataSet']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'storybase_asset.htmlasset': {
            'Meta': {'object_name': 'HtmlAsset', '_ormbases': ['storybase_asset.Asset']},
            'asset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.Asset']", 'unique': 'True', 'primary_key': 'True'})
        },
        'storybase_asset.htmlassettranslation': {
            'Meta': {'unique_together': "(('asset', 'language'),)", 'object_name': 'HtmlAssetTranslation'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_asset_htmlassettranslation_related'", 'to': "orm['storybase_asset.Asset']"}),
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'title': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        'storybase_asset.localdataset': {
            'Meta': {'object_name': 'LocalDataSet', '_ormbases': ['storybase_asset.DataSet']},
            'dataset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.DataSet']", 'unique': 'True', 'primary_key': 'True'}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.File']"})
        },
        'storybase_asset.localimageasset': {
            'Meta': {'object_name': 'LocalImageAsset', '_ormbases': ['storybase_asset.Asset']},
            'asset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['storybase_asset.Asset']", 'unique': 'True', 'primary_key': 'True'})
        },
        'storybase_asset.localimageassettranslation': {
            'Meta': {'unique_together': "(('asset', 'language'),)", 'object_name': 'LocalImageAssetTranslation'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_asset_localimageassettranslation_related'", 'to': "orm['storybase_asset.Asset']"}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['filer.Image']"}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'title': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        }
    }

    complete_apps = ['storybase_asset']
