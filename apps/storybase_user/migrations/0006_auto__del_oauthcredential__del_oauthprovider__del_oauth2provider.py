# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'OAuthCredential'
        db.delete_table('storybase_user_oauthcredential')

        # Deleting model 'OAuthProvider'
        db.delete_table('storybase_user_oauthprovider')

        # Deleting model 'OAuth2Provider'
        db.delete_table('storybase_user_oauth2provider')


    def backwards(self, orm):
        
        # Adding model 'OAuthCredential'
        db.create_table('storybase_user_oauthcredential', (
            ('token', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='storybase_user_oauthcredential_credentials', to=orm['auth.User'])),
            ('provider', self.gf('django.db.models.fields.related.ForeignKey')(related_name='credentials', to=orm['storybase_user.OAuthProvider'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('storybase_user', ['OAuthCredential'])

        # Adding model 'OAuthProvider'
        db.create_table('storybase_user_oauthprovider', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('client_secret', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('authorize_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('client_token', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('request_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('access_token_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('storybase_user', ['OAuthProvider'])

        # Adding model 'OAuth2Provider'
        db.create_table('storybase_user_oauth2provider', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('base_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('client_secret', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('storybase_user', ['OAuth2Provider'])


    models = {
        
    }

    complete_apps = ['storybase_user']
