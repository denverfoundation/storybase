# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

from apps.utils import transform, to_uuid, to_char32


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_help', '0001_initial'),
    ]

    operations = [
        # Help.help_id
        migrations.AddField(
            model_name='help',
            name='tmp_help_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_help', 'Help', 'help_id'),
            transform(to_char32, 'storybase_help', 'Help', 'help_id'),
        ),
        migrations.RemoveField(
            model_name='help',
            name='help_id',
        ),
        migrations.RenameField(
            model_name='help',
            old_name='tmp_help_id',
            new_name='help_id',
        ),
        migrations.AlterField(
            model_name='help',
            name='help_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # HelpTranslation.translation_id
        migrations.AddField(
            model_name='helptranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_help', 'HelpTranslation', 'translation_id'),
            transform(to_char32, 'storybase_help', 'HelpTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='helptranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='helptranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='helptranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),
    ]
