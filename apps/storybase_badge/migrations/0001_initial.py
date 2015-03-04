# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Badge'
        db.create_table(u'storybase_badge_badge', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('icon_uri', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'storybase_badge', ['Badge'])


    def backwards(self, orm):
        # Deleting model 'Badge'
        db.delete_table(u'storybase_badge_badge')


    models = {
        u'storybase_badge.badge': {
            'Meta': {'object_name': 'Badge'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'icon_uri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['storybase_badge']