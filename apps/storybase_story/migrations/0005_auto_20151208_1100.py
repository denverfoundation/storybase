# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_story', '0004_auto_20151013_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storyrelation',
            name='relation_type',
            field=models.CharField(default=b'connected', max_length=25, choices=[(b'connected', 'Connected Story'), (b'relevant', 'Relevant Story')]),
        ),
    ]
