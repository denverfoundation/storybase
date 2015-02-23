# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing M2M table for field stories on 'Badge'
        db.delete_table(db.shorten_name(u'storybase_badge_badge_stories'))

        # Removing M2M table for field users on 'Badge'
        db.delete_table(db.shorten_name(u'storybase_badge_badge_users'))


    def backwards(self, orm):
        # Adding M2M table for field stories on 'Badge'
        m2m_table_name = db.shorten_name(u'storybase_badge_badge_stories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('badge', models.ForeignKey(orm[u'storybase_badge.badge'], null=False)),
            ('story', models.ForeignKey(orm[u'storybase_story.story'], null=False))
        ))
        db.create_unique(m2m_table_name, ['badge_id', 'story_id'])

        # Adding M2M table for field users on 'Badge'
        m2m_table_name = db.shorten_name(u'storybase_badge_badge_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('badge', models.ForeignKey(orm[u'storybase_badge.badge'], null=False)),
            ('userprofile', models.ForeignKey(orm[u'storybase_user.userprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['badge_id', 'userprofile_id'])


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