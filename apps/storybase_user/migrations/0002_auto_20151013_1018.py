# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

from apps.utils import transform, to_uuid, to_char32


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_user', '0001_initial'),
    ]

    operations = [
        # Organization.organization_id
        migrations.AddField(
            model_name='organization',
            name='tmp_organization_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_user', 'Organization', 'organization_id'),
            transform(to_char32, 'storybase_user', 'Organization', 'organization_id'),
        ),
        migrations.RemoveField(
            model_name='organization',
            name='organization_id',
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='tmp_organization_id',
            new_name='organization_id',
        ),
        migrations.AlterField(
            model_name='organization',
            name='organization_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # OrganizationTranslation.translation_id
        migrations.AddField(
            model_name='organizationtranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_user', 'OrganizationTranslation', 'translation_id'),
            transform(to_char32, 'storybase_user', 'OrganizationTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='organizationtranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='organizationtranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='organizationtranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # Project.project_id
        migrations.AddField(
            model_name='project',
            name='tmp_project_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_user', 'Project', 'project_id'),
            transform(to_char32, 'storybase_user', 'Project', 'project_id'),
        ),
        migrations.RemoveField(
            model_name='project',
            name='project_id',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='tmp_project_id',
            new_name='project_id',
        ),
        migrations.AlterField(
            model_name='project',
            name='project_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # ProjectTranslation.translation_id
        migrations.AddField(
            model_name='projecttranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_user', 'ProjectTranslation', 'translation_id'),
            transform(to_char32, 'storybase_user', 'ProjectTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='projecttranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='projecttranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='projecttranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # UserProfile.profile_id
        migrations.AddField(
            model_name='userprofile',
            name='tmp_profile_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_user', 'UserProfile', 'profile_id'),
            transform(to_char32, 'storybase_user', 'UserProfile', 'profile_id'),
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='profile_id',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='tmp_profile_id',
            new_name='profile_id',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),
    ]
