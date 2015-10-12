# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_geo', '0001_initial'),
        ('storybase_user', '0001_initial'),
        ('storybase_story', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='organizations',
            field=models.ManyToManyField(related_name='stories', to='storybase_user.Organization', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='story',
            name='places',
            field=models.ManyToManyField(related_name='stories', verbose_name='Places', to='storybase_geo.Place', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='story',
            name='projects',
            field=models.ManyToManyField(related_name='stories', to='storybase_user.Project', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='story',
            name='related_stories',
            field=models.ManyToManyField(related_name='related_to', through='storybase_story.StoryRelation', to='storybase_story.Story', blank=True),
            preserve_default=True,
        ),
    ]
