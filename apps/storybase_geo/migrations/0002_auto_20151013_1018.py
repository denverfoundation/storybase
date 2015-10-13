# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_geo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='location_id',
            field=models.UUIDField(default=uuid.uuid4, verbose_name='Location ID', db_index=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='place_id',
            field=models.UUIDField(default=uuid.uuid4, verbose_name='Place ID', db_index=True),
        ),
    ]
