# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

from apps.utils import transform, to_uuid, to_char32


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_story', '0003_auto_20151012_1713'),
    ]

    operations = [
        # ContainerTemplate.template_id
        migrations.AddField(
            model_name='containertemplate',
            name='tmp_container_template_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'ContainerTemplate', 'container_template_id'),
            transform(to_char32, 'storybase_story', 'ContainerTemplate', 'container_template_id'),
        ),
        migrations.RemoveField(
            model_name='containertemplate',
            name='container_template_id',
        ),
        migrations.RenameField(
            model_name='containertemplate',
            old_name='tmp_container_template_id',
            new_name='container_template_id',
        ),
        migrations.AlterField(
            model_name='containertemplate',
            name='container_template_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # Section.section_id
        migrations.AddField(
            model_name='section',
            name='tmp_section_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'Section', 'section_id'),
            transform(to_char32, 'storybase_story', 'Section', 'section_id'),
        ),
        migrations.RemoveField(
            model_name='section',
            name='section_id',
        ),
        migrations.RenameField(
            model_name='section',
            old_name='tmp_section_id',
            new_name='section_id',
        ),
        migrations.AlterField(
            model_name='section',
            name='section_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # SectionLayout.layout_id
        migrations.AddField(
            model_name='sectionlayout',
            name='tmp_layout_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'SectionLayout', 'layout_id'),
            transform(to_char32, 'storybase_story', 'SectionLayout', 'layout_id'),
        ),
        migrations.RemoveField(
            model_name='sectionlayout',
            name='layout_id',
        ),
        migrations.RenameField(
            model_name='sectionlayout',
            old_name='tmp_layout_id',
            new_name='layout_id',
        ),
        migrations.AlterField(
            model_name='sectionlayout',
            name='layout_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # SectionLayoutTranslation.translation_id
        migrations.AddField(
            model_name='sectionlayouttranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'SectionLayoutTranslation', 'translation_id'),
            transform(to_char32, 'storybase_story', 'SectionLayoutTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='sectionlayouttranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='sectionlayouttranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='sectionlayouttranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # SectionTranslation.translation_id
        migrations.AddField(
            model_name='sectiontranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'SectionTranslation', 'translation_id'),
            transform(to_char32, 'storybase_story', 'SectionTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='sectiontranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='sectiontranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='sectiontranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # Story.story_id
        migrations.AddField(
            model_name='story',
            name='tmp_story_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'Story', 'story_id'),
            transform(to_char32, 'storybase_story', 'Story', 'story_id'),
        ),
        migrations.RemoveField(
            model_name='story',
            name='story_id',
        ),
        migrations.RenameField(
            model_name='story',
            old_name='tmp_story_id',
            new_name='story_id',
        ),
        migrations.AlterField(
            model_name='story',
            name='story_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # StoryRelation.relation_id
        migrations.AddField(
            model_name='storyrelation',
            name='tmp_relation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'StoryRelation', 'relation_id'),
            transform(to_char32, 'storybase_story', 'StoryRelation', 'relation_id'),
        ),
        migrations.RemoveField(
            model_name='storyrelation',
            name='relation_id',
        ),
        migrations.RenameField(
            model_name='storyrelation',
            old_name='tmp_relation_id',
            new_name='relation_id',
        ),
        migrations.AlterField(
            model_name='storyrelation',
            name='relation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # StoryTemplate.template_id
        migrations.AddField(
            model_name='storytemplate',
            name='tmp_template_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'StoryTemplate', 'template_id'),
            transform(to_char32, 'storybase_story', 'StoryTemplate', 'template_id'),
        ),
        migrations.RemoveField(
            model_name='storytemplate',
            name='template_id',
        ),
        migrations.RenameField(
            model_name='storytemplate',
            old_name='tmp_template_id',
            new_name='template_id',
        ),
        migrations.AlterField(
            model_name='storytemplate',
            name='template_id',
            field=models.UUIDField(null=False, default=uuid.uuid4, db_index=True),
        ),

        # StoryTemplateTranslation.translation_id
        migrations.AddField(
            model_name='storytemplatetranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'StoryTemplateTranslation', 'translation_id'),
            transform(to_char32, 'storybase_story', 'StoryTemplateTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='storytemplatetranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='storytemplatetranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='storytemplatetranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),

        # StoryTranslation.translation_id
        migrations.AddField(
            model_name='storytranslation',
            name='tmp_translation_id',
            field=models.UUIDField(null=True, default=None),
        ),
        migrations.RunPython(
            transform(to_uuid, 'storybase_story', 'StoryTranslation', 'translation_id'),
            transform(to_char32, 'storybase_story', 'StoryTranslation', 'translation_id'),
        ),
        migrations.RemoveField(
            model_name='storytranslation',
            name='translation_id',
        ),
        migrations.RenameField(
            model_name='storytranslation',
            old_name='tmp_translation_id',
            new_name='translation_id',
        ),
        migrations.AlterField(
            model_name='storytranslation',
            name='translation_id',
            field=models.UUIDField(null=False, default=uuid.uuid4),
        ),
    ]
