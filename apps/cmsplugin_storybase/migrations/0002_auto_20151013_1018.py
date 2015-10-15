# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

from apps.utils import transform, to_uuid, to_char32


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_storybase', '0001_initial'),
    ]

    operations = [
        # ActivityTranslation.translation_id
        migrations.AddField(
            model_name='activitytranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'cmsplugin_storybase', 'ActivityTranslation', 'translation_id'),
            transform(to_char32, 'cmsplugin_storybase', 'ActivityTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='activitytranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='activitytranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='activitytranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # NewsItemTranslation.translation_id
        migrations.AddField(
            model_name='newsitemtranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'cmsplugin_storybase', 'NewsItemTranslation', 'translation_id'),
            transform(to_char32, 'cmsplugin_storybase', 'NewsItemTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='newsitemtranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='newsitemtranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='newsitemtranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='newsitemtranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
