# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cmsplugin_storybase.models
import filer.fields.image
from django.conf import settings
import uuidfield.fields
import storybase.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('filer', '0002_auto_20150606_2003'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storybase_story', '0003_auto_20151012_1713'),
        ('storybase_help', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='A short, unique label for this activity. It is also used to build URLs for the activity. This field can only contain letters, numbers, underscores or hyphens', blank=True)),
                ('image', filer.fields.image.FilerImageField(blank=True, to='filer.Image', help_text='Image used as the thumbnail when activities are listed. Additional images can be shown on the related CMS page', null=True)),
                ('page', models.OneToOneField(null=True, blank=True, to='cms.Page', help_text='CMS page that provides additional, free-form information about thei activity')),
            ],
            options={
                'verbose_name_plural': 'Activities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActivityPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('activity', models.ForeignKey(related_name='plugins', to='cmsplugin_storybase.Activity')),
            ],
            options={
                'abstract': False,
                'db_table': 'cmsplugin_activityplugin',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='ActivityTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField()),
                ('description', models.TextField()),
                ('supplies', models.TextField(verbose_name='Required supplies', blank=True)),
                ('time', models.CharField(max_length=200, verbose_name='Time it takes to do', blank=True)),
                ('num_participants', models.CharField(max_length=200, verbose_name='Number of participants', blank=True)),
                ('links', models.TextField(help_text='These are materials/handouts we have been using in Story-Rasings', verbose_name='Links to the full activity', blank=True)),
                ('activity', models.ForeignKey(to='cmsplugin_storybase.Activity')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HelpPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('help', models.ForeignKey(related_name='plugins', to='storybase_help.Help')),
            ],
            options={
                'abstract': False,
                'db_table': 'cmsplugin_helpplugin',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('num_items', models.IntegerField(default=3)),
            ],
            options={
                'abstract': False,
                'db_table': 'cmsplugin_list',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default='draft', max_length=10, choices=[('pending', 'pending'), ('draft', 'draft'), ('staged', 'staged'), ('published', 'published')])),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(blank=True)),
                ('on_homepage', models.BooleanField(default=False, verbose_name='Featured on homepage')),
                ('author', models.ForeignKey(related_name='news_items', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(cmsplugin_storybase.models.NewsItemPermission, models.Model),
        ),
        migrations.CreateModel(
            name='NewsItemTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('image', filer.fields.image.FilerImageField(to='filer.Image', null=True)),
                ('news_item', models.ForeignKey(to='cmsplugin_storybase.NewsItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('story', models.ForeignKey(related_name='plugins', to='storybase_story.Story')),
            ],
            options={
                'abstract': False,
                'db_table': 'cmsplugin_storyplugin',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Teaser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('teaser', models.TextField(blank=True)),
                ('language', models.CharField(max_length=15, verbose_name='language', db_index=True)),
                ('page', models.ForeignKey(related_name='teaser_set', verbose_name='page', to='cms.Page')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='teaser',
            unique_together=set([('language', 'page')]),
        ),
        migrations.AlterUniqueTogether(
            name='newsitemtranslation',
            unique_together=set([('news_item', 'language')]),
        ),
    ]
