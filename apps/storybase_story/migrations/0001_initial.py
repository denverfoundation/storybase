# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import storybase_asset.models
import storybase.fields
import django_dag.models
from django.conf import settings
import uuidfield.fields
import storybase_story.models
import storybase.models.dirtyfields


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_geo', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storybase_asset', '0001_initial'),
        ('storybase_badge', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContainerTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('container_template_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('asset_type', models.CharField(blank=True, help_text='Default asset type', max_length=10, choices=[('image', 'image'), ('audio', 'audio'), ('video', 'video'), ('map', 'map'), ('chart', 'chart'), ('table', 'table'), ('quotation', 'quotation'), ('text', 'text')])),
                ('can_change_asset_type', models.BooleanField(default=False, help_text='User can change the asset type from the default')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('root', models.BooleanField(default=False)),
                ('weight', models.IntegerField(default=0, help_text='The ordering of top-level sections relative to each other. Sections with lower weight values are shown before ones with higher weight values in lists.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, django_dag.models.NodeBase, storybase_story.models.SectionPermission),
        ),
        migrations.CreateModel(
            name='SectionAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model, storybase_story.models.SectionAssetPermission),
        ),
        migrations.CreateModel(
            name='SectionLayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('layout_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('template', models.CharField(max_length=100, verbose_name='template', choices=[(b'side_by_side.html', b'side_by_side.html'), (b'1_up.html', b'1_up.html'), (b'above_below.html', b'above_below.html'), (b'3_stacked.html', b'3_stacked.html')])),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionLayoutTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('name', storybase.fields.ShortTextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SectionTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('license', models.CharField(blank=True, max_length=25, choices=[(b'CC BY-NC-SA', 'Attribution-NonCommercial-ShareAlike Creative Commons'), (b'CC BY-NC', 'Attribution-NonCommercial Creative Commons'), (b'CC BY-NC-ND', 'Attribution-NonCommercial-NoDerivs Creative Commons'), (b'CC BY', 'Attribution Creative Commons'), (b'CC BY-SA', 'Attribution-ShareAlike Creative Commons'), (b'CC BY-ND', 'Attribution-NoDerivs Creative Commons'), (b'none', 'None (All rights reserved)')])),
                ('status', models.CharField(default='draft', max_length=10, choices=[('pending', 'pending'), ('draft', 'draft'), ('staged', 'staged'), ('published', 'published')])),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('weight', models.IntegerField(default=0)),
                ('story_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('slug', models.SlugField(blank=True)),
                ('byline', models.TextField()),
                ('structure_type', models.CharField(max_length=20, verbose_name='structure', choices=[(b'spider', b'Spider'), (b'linear', b'Linear')])),
                ('is_template', models.BooleanField(default=False, verbose_name='Story is a template')),
                ('allow_connected', models.BooleanField(default=False, verbose_name='Story can have connected stories')),
                ('on_homepage', models.BooleanField(default=False, verbose_name='Featured on homepage')),
                ('contact_info', models.TextField(verbose_name='Contact Information', blank=True)),
                ('assets', models.ManyToManyField(related_name='stories', to='storybase_asset.Asset', blank=True)),
                ('author', models.ForeignKey(related_name='stories', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('badges', models.ManyToManyField(related_name='stories', to='storybase_badge.Badge')),
                ('datasets', models.ManyToManyField(related_name='stories', to='storybase_asset.DataSet', blank=True)),
                ('featured_assets', models.ManyToManyField(help_text='Assets to be displayed in teaser version of Story', related_name='featured_in_stories', to='storybase_asset.Asset', blank=True)),
                ('locations', models.ManyToManyField(related_name='stories', verbose_name='Locations', to='storybase_geo.Location', blank=True)),
            ],
            options={
                'verbose_name_plural': 'stories',
            },
            bases=(storybase_asset.models.FeaturedAssetsMixin, storybase.models.dirtyfields.TzDirtyFieldsMixin, models.Model, storybase_story.models.StoryPermission),
        ),
        migrations.CreateModel(
            name='StoryRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relation_id', uuidfield.fields.UUIDField(auto=True)),
                ('relation_type', models.CharField(default=b'connected', max_length=25, choices=[(b'connected', 'Connected Story')])),
                ('source', models.ForeignKey(related_name='target', to='storybase_story.Story')),
                ('target', models.ForeignKey(related_name='source', to='storybase_story.Story')),
            ],
            options={
            },
            bases=(storybase_story.models.StoryRelationPermission, models.Model),
        ),
        migrations.CreateModel(
            name='StoryTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('time_needed', models.CharField(blank=True, help_text='The amount of time needed to create a story of this type', max_length=140, choices=[(b'5 minutes', '5 minutes'), (b'30 minutes', '30 minutes')])),
                ('level', models.CharField(blank=True, help_text='The level of storytelling experience suggested to create stories with this template', max_length=140, choices=[(b'beginner', 'Beginner')])),
                ('slug', models.SlugField(help_text='A human-readable unique identifier', unique=True)),
                ('examples', models.ManyToManyField(help_text='Stories that are examples of this template', related_name='example_for', null=True, to='storybase_story.Story', blank=True)),
                ('story', models.ForeignKey(blank=True, to='storybase_story.Story', help_text='The story that provides the structure for this template', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryTemplateTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField()),
                ('tag_line', storybase.fields.ShortTextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('ingredients', storybase.fields.ShortTextField(blank=True)),
                ('best_for', storybase.fields.ShortTextField(blank=True)),
                ('tip', storybase.fields.ShortTextField(blank=True)),
                ('story_template', models.ForeignKey(to='storybase_story.StoryTemplate')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StoryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField(blank=True)),
                ('summary', models.TextField(blank=True)),
                ('call_to_action', models.TextField(verbose_name='Call to Action', blank=True)),
                ('connected_prompt', models.TextField(verbose_name='Connected Story Prompt', blank=True)),
                ('story', models.ForeignKey(to='storybase_story.Story')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='storytranslation',
            unique_together=set([('story', 'language')]),
        ),
    ]
