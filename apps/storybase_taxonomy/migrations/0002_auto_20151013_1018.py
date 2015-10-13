# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_taxonomy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorytranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='tag',
            name='tag_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
