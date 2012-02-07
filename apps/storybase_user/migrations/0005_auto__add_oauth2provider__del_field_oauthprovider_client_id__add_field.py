# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'OAuth2Provider'
        db.create_table('storybase_user_oauth2provider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('base_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('client_secret', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('storybase_user', ['OAuth2Provider'])

        # Deleting field 'OAuthProvider.client_id'
        db.delete_column('storybase_user_oauthprovider', 'client_id')

        # Adding field 'OAuthProvider.client_token'
        db.add_column('storybase_user_oauthprovider', 'client_token', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'OAuth2Provider'
        db.delete_table('storybase_user_oauth2provider')

        # User chose to not deal with backwards NULL issues for 'OAuthProvider.client_id'
        raise RuntimeError("Cannot reverse this migration. 'OAuthProvider.client_id' and its values cannot be restored.")

        # Deleting field 'OAuthProvider.client_token'
        db.delete_column('storybase_user_oauthprovider', 'client_token')


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
        'storybase_user.oauth2provider': {
            'Meta': {'object_name': 'OAuth2Provider'},
            'base_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'client_secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'storybase_user.oauthcredential': {
            'Meta': {'object_name': 'OAuthCredential'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credentials'", 'to': "orm['storybase_user.OAuthProvider']"}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'storybase_user_oauthcredential_credentials'", 'to': "orm['auth.User']"})
        },
        'storybase_user.oauthprovider': {
            'Meta': {'object_name': 'OAuthProvider'},
            'access_token_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'authorize_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'client_secret': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'client_token': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'request_token_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['storybase_user']
