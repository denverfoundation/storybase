# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_story', '0005_auto_20151208_1100'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='storyrelation',
            unique_together=set([('source', 'target')]),
        ),
    ]
