# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

from apps.utils import transform, to_uuid, to_char32


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_asset', '0001_initial'),
    ]

    operations = [
        # Asset.asset_id
        migrations.AddField(
            model_name='asset',
            name='tmp_asset_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_asset', 'Asset', 'asset_id'),
            transform(to_char32, 'storybase_asset', 'Asset', 'asset_id'),
        ),
        migrations.RemoveField(
            model_name='asset',
            name='asset_id',
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='tmp_asset_id',
            new_name='asset_id',
        ),
        migrations.AlterField(
            model_name='asset',
            name='asset_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # DataSet.dataset_id
        migrations.AddField(
            model_name='dataset',
            name='tmp_dataset_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_asset', 'DataSet', 'dataset_id'),
            transform(to_char32, 'storybase_asset', 'DataSet', 'dataset_id'),
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='dataset_id',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='tmp_dataset_id',
            new_name='dataset_id',
        ),
        migrations.AlterField(
            model_name='dataset',
            name='dataset_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # DataSetTranslation.translation_id
        migrations.AddField(
            model_name='datasettranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_asset', 'DataSetTranslation', 'translation_id'),
            transform(to_char32, 'storybase_asset', 'DataSetTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='datasettranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='datasettranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='datasettranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # ExternalAssetTranslation.translation_id
        migrations.AddField(
            model_name='externalassettranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_asset', 'ExternalAssetTranslation', 'translation_id'),
            transform(to_char32, 'storybase_asset', 'ExternalAssetTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='externalassettranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='externalassettranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='externalassettranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # HtmlAssetTranslation.translation_id
        migrations.AddField(
            model_name='htmlassettranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_asset', 'HtmlAssetTranslation', 'translation_id'),
            transform(to_char32, 'storybase_asset', 'HtmlAssetTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='htmlassettranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='htmlassettranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='htmlassettranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # LocalImageAssetTranslation.translation_id
        migrations.AddField(
            model_name='localimageassettranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_asset', 'LocalImageAssetTranslation', 'translation_id'),
            transform(to_char32, 'storybase_asset', 'LocalImageAssetTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='localimageassettranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='localimageassettranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='localimageassettranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),
    ]
