# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import storybase.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_storybase', '0007_partnertranslation_partner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partnertranslation',
            name='name',
        ),
        migrations.AddField(
            model_name='partner',
            name='name',
            field=storybase.fields.ShortTextField(default=''),
            preserve_default=False,
        ),
    ]
