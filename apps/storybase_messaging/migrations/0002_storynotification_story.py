# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_messaging', '0001_initial'),
        ('storybase_story', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='storynotification',
            name='story',
            field=models.ForeignKey(to='storybase_story.Story'),
            preserve_default=True,
        ),
    ]
