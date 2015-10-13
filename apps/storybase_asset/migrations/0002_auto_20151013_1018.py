# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_asset', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='asset_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='dataset_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='datasettranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='externalassettranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='htmlassettranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='localimageassettranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
