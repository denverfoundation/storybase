# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'FilerImageAsset'
        db.delete_table('storybase_asset_filerimageasset')

        # Deleting model 'ExternalAsset'
        db.delete_table('storybase_asset_externalasset')

        # Adding model 'HtmlAssetTranslation'
        db.create_table('storybase_asset_htmlassettranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_asset_htmlassettranslation_related', to=orm['storybase_asset.Asset'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('storybase_asset', ['HtmlAssetTranslation'])

        # Adding unique constraint on 'HtmlAssetTranslation', fields ['asset', 'language']
        db.create_unique('storybase_asset_htmlassettranslation', ['asset_id', 'language'])

        # Deleting field 'HtmlAsset.body'
        db.delete_column('storybase_asset_htmlasset', 'body')

        # Adding M2M table for field translations on 'HtmlAsset'
        db.create_table('storybase_asset_htmlasset_translations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('htmlasset', models.ForeignKey(orm['storybase_asset.htmlasset'], null=False)),
            ('htmlassettranslation', models.ForeignKey(orm['storybase_asset.htmlassettranslation'], null=False))
        ))
        db.create_unique('storybase_asset_htmlasset_translations', ['htmlasset_id', 'htmlassettranslation_id'])

        # Deleting field 'Asset.title'
        db.delete_column('storybase_asset_asset', 'title')

        # Deleting field 'Asset.caption'
        db.delete_column('storybase_asset_asset', 'caption')

        # Deleting field 'Asset.user'
        db.delete_column('storybase_asset_asset', 'user_id')

        # Adding field 'Asset.owner'
        db.add_column('storybase_asset_asset', 'owner', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='assets', to=orm['auth.User']), keep_default=False)


    def backwards(self, orm):
        
        # Removing unique constraint on 'HtmlAssetTranslation', fields ['asset', 'language']
        db.delete_unique('storybase_asset_htmlassettranslation', ['asset_id', 'language'])

        # Adding model 'FilerImageAsset'
        db.create_table('storybase_asset_filerimageasset', (
            ('asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.Asset'], unique=True, primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['filer.Image'])),
        ))
        db.send_create_signal('storybase_asset', ['FilerImageAsset'])

        # Adding model 'ExternalAsset'
        db.create_table('storybase_asset_externalasset', (
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('asset_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['storybase_asset.Asset'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('storybase_asset', ['ExternalAsset'])

        # Deleting model 'HtmlAssetTranslation'
        db.delete_table('storybase_asset_htmlassettranslation')

        # Adding field 'HtmlAsset.body'
        db.add_column('storybase_asset_htmlasset', 'body', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # Removing M2M table for field translations on 'HtmlAsset'
        db.delete_table('storybase_asset_htmlasset_translations')

        # Adding field 'Asset.title'
        db.add_column('storybase_asset_asset', 'title', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Asset.caption'
        db.add_column('storybase_asset_asset', 'caption', self.gf('django.db.models.fields.TextField')(default='', blank=True), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'Asset.user'
        raise RuntimeError("Cannot reverse this migration. 'Asset.user' and its values cannot be restored.")

        # Deleting field 'Asset.owner'
        db.delete_column('storybase_asset_asset', 'owner_id')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assets'", 'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
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
