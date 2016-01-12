# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image
import storybase.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        ('cmsplugin_storybase', '0004_auto_20160112_0737'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', filer.fields.image.FilerImageField(blank=True, to='filer.Image', help_text="Image of the partner's logo.", null=True)),
            ],
            options={
                'verbose_name_plural': 'Partners',
            },
        ),
        migrations.CreateModel(
            name='PartnerTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', models.UUIDField(default=uuid.uuid4)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', 'English'), (b'es', 'Spanish')])),
                ('name', storybase.fields.ShortTextField()),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
