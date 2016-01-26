# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_story', '0006_auto_20151208_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='badges',
            field=models.ManyToManyField(related_name='stories', to='storybase_badge.Badge', blank=True),
        ),
    ]
