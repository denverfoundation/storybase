# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards(apps, schema_editor):
    Title = apps.get_model('cms', 'Title')
    Teaser = apps.get_model('cmsplugin_storybase', 'Teaser')
    TeaserExtension = apps.get_model('cmsplugin_storybase', 'TeaserExtension')

    db_alias = schema_editor.connection.alias

    for teaser in Teaser.objects.using(db_alias).all():
        try:
            title = Title.objects.get(page=teaser.page, language=teaser.language)
            TeaserExtension.objects.get_or_create(extended_object=title,
                                                  teaser=teaser.teaser)
        except Title.DoesNotExist:
            pass

def backwards(apps, schema_editor):
    Teaser = apps.get_model('cmsplugin_storybase', 'Teaser')
    TeaserExtension = apps.get_model('cmsplugin_storybase', 'TeaserExtension')

    db_alias = schema_editor.connection.alias

    for extension in TeaserExtension.objects.using(db_alias).all():
        Teaser.objects.get_or_create(teaser=extension.teaser,
                                     language=extension.extended_object.language,
                                     page=extension.extended_object.page)


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('cmsplugin_storybase', '0002_auto_20151013_1018'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeaserExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('teaser', models.TextField(help_text='Brief description of the page to be included on parent pages', blank=True)),
                ('extended_object', models.OneToOneField(editable=False, to='cms.Title')),
                ('public_extension', models.OneToOneField(related_name='draft_extension', null=True, editable=False, to='cmsplugin_storybase.TeaserExtension')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(forwards, backwards),
        migrations.DeleteModel('Teaser'),
    ]
