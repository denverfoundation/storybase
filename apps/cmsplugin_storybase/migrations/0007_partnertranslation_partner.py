# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_storybase', '0006_partnerplugin'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnertranslation',
            name='partner',
            field=models.ForeignKey(default=1, to='cmsplugin_storybase.Partner'),
            preserve_default=False,
        ),
    ]
