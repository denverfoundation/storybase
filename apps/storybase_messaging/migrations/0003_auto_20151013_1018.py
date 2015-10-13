# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_messaging', '0002_storynotification_story'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitecontactmessage',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Your Email'),
        ),
        migrations.AlterField(
            model_name='systemmessagetranslation',
            name='translation_id',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
