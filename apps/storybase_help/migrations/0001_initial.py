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
            name='Help',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('help_id', uuidfield.fields.UUIDField(auto=True)),
                ('slug', models.SlugField(blank=True)),
                ('searchable', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'help items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HelpTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('help', models.ForeignKey(to='storybase_help.Help')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
