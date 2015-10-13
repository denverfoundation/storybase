# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='organization_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='organizationtranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='projecttranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
    ]
