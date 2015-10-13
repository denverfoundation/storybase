# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_story', '0003_auto_20151012_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='containertemplate',
            name='container_template_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='section_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='sectionlayout',
            name='layout_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='sectionlayouttranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='sectiontranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='story',
            name='story_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='storyrelation',
            name='relation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='storytemplate',
            name='template_id',
            field=models.UUIDField(default=uuid.uuid4, db_index=True),
        ),
        migrations.AlterField(
            model_name='storytemplatetranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='storytranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
