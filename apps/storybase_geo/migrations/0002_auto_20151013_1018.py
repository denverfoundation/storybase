# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

from apps.utils import transform, to_uuid, to_char32


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_geo', '0001_initial'),
    ]

    operations = [
        # Location.location_id
        migrations.AddField(
            model_name='location',
            name='tmp_location_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_geo', 'Location', 'location_id'),
            transform(to_char32, 'storybase_geo', 'Location', 'location_id'),
        ),
        migrations.RemoveField(
            model_name='location',
            name='location_id',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='tmp_location_id',
            new_name='location_id',
        ),
        migrations.AlterField(
            model_name='location',
            name='location_id',
            field=models.UUIDField(null=False, default=uuid.uuid4,
                                   verbose_name='Location ID', db_index=True),
        ),

        # Place.place_id
        migrations.AddField(
            model_name='place',
            name='tmp_place_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_geo', 'Place', 'place_id'),
            transform(to_char32, 'storybase_geo', 'Place', 'place_id'),
        ),
        migrations.RemoveField(
            model_name='place',
            name='place_id',
        ),
        migrations.RenameField(
            model_name='place',
            old_name='tmp_place_id',
            new_name='place_id',
        ),
        migrations.AlterField(
            model_name='place',
            name='place_id',
            field=models.UUIDField(null=False, default=uuid.uuid4,
                                   verbose_name='Place ID', db_index=True),
        ),
    ]
