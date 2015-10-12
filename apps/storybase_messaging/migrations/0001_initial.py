# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields
import storybase.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteContactMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', storybase.fields.ShortTextField(verbose_name='Your Name')),
                ('email', models.EmailField(max_length=75, verbose_name='Your Email')),
                ('phone', models.CharField(max_length=20, verbose_name='Your Phone Number', blank=True)),
                ('message', models.TextField(verbose_name='Your Message')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Message Created')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notification_type', models.CharField(max_length=25, choices=[(b'unpublished', b'Reminder of unpublished story'), (b'published', b'Reminder of published stories')])),
                ('sent', models.DateTimeField(null=True, blank=True)),
                ('send_on', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SystemMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('sent', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SystemMessageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('subject', storybase.fields.ShortTextField()),
                ('body', models.TextField()),
                ('message', models.ForeignKey(to='storybase_messaging.SystemMessage')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
