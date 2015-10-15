# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

from apps.utils import transform, to_uuid, to_char32


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_taxonomy', '0001_initial'),
    ]

    operations = [
        # CategoryTranslation.translation_id
        migrations.AddField(
            model_name='categorytranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_taxonomy', 'CategoryTranslation', 'translation_id'),
            transform(to_char32, 'storybase_taxonomy', 'CategoryTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='categorytranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='categorytranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='categorytranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # Tag.tag_id
        migrations.AddField(
            model_name='tag',
            name='tmp_tag_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_taxonomy', 'Tag', 'tag_id'),
            transform(to_char32, 'storybase_taxonomy', 'Tag', 'tag_id'),
        ),
        migrations.RemoveField(
            model_name='tag',
            name='tag_id',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='tmp_tag_id',
            new_name='tag_id',
        ),
        migrations.AlterField(
            model_name='tag',
            name='tag_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),
    ]
