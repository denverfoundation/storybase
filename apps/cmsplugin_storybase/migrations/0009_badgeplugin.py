# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0014_auto_20160404_1908'),
        ('storybase_badge', '0001_initial'),
        ('cmsplugin_storybase', '0008_auto_20160112_1433'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgePlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('badge', models.ForeignKey(related_name='badges', to='storybase_badge.Badge')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
