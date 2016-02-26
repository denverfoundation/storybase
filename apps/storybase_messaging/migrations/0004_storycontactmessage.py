# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_story', '0007_auto_20160126_0923'),
        ('storybase_messaging', '0003_auto_20151013_1018'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoryContactMessage',
            fields=[
                ('sitecontactmessage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='storybase_messaging.SiteContactMessage')),
                ('story', models.ForeignKey(to='storybase_story.Story')),
            ],
            bases=('storybase_messaging.sitecontactmessage',),
        ),
    ]
