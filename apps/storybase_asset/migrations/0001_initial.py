# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filer.fields.file
import storybase_asset.models
import filer.fields.image
from django.conf import settings
import uuidfield.fields
import storybase.fields


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0002_auto_20150606_2003'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('license', models.CharField(blank=True, max_length=25, choices=[(b'CC BY-NC-SA', 'Attribution-NonCommercial-ShareAlike Creative Commons'), (b'CC BY-NC', 'Attribution-NonCommercial Creative Commons'), (b'CC BY-NC-ND', 'Attribution-NonCommercial-NoDerivs Creative Commons'), (b'CC BY', 'Attribution Creative Commons'), (b'CC BY-SA', 'Attribution-ShareAlike Creative Commons'), (b'CC BY-ND', 'Attribution-NoDerivs Creative Commons'), (b'none', 'None (All rights reserved)')])),
                ('status', models.CharField(default='draft', max_length=10, choices=[('pending', 'pending'), ('draft', 'draft'), ('staged', 'staged'), ('published', 'published')])),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('asset_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('type', models.CharField(max_length=10, choices=[('image', 'image'), ('audio', 'audio'), ('video', 'video'), ('map', 'map'), ('chart', 'chart'), ('table', 'table'), ('quotation', 'quotation'), ('text', 'text')])),
                ('attribution', models.TextField(blank=True)),
                ('source_url', models.URLField(blank=True)),
                ('section_specific', models.BooleanField(default=False)),
                ('asset_created', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(storybase_asset.models.ImageRenderingMixin, models.Model, storybase_asset.models.AssetPermission),
        ),
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default='draft', max_length=10, choices=[('pending', 'pending'), ('draft', 'draft'), ('staged', 'staged'), ('published', 'published')])),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('dataset_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('source', models.TextField(blank=True)),
                ('attribution', models.TextField(blank=True)),
                ('links_to_file', models.BooleanField(default=True, verbose_name='Links to file')),
                ('dataset_created', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, storybase_asset.models.DataSetPermission),
        ),
        migrations.CreateModel(
            name='DataSetTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField()),
                ('description', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExternalAsset',
            fields=[
                ('asset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='storybase_asset.Asset')),
            ],
            options={
                'abstract': False,
            },
            bases=('storybase_asset.asset',),
        ),
        migrations.CreateModel(
            name='ExternalAssetTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField(blank=True)),
                ('caption', models.TextField(blank=True)),
                ('url', models.URLField(max_length=500)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExternalDataSet',
            fields=[
                ('dataset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='storybase_asset.DataSet')),
                ('url', models.URLField()),
            ],
            options={
                'abstract': False,
            },
            bases=('storybase_asset.dataset',),
        ),
        migrations.CreateModel(
            name='HtmlAsset',
            fields=[
                ('asset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='storybase_asset.Asset')),
            ],
            options={
                'abstract': False,
            },
            bases=('storybase_asset.asset',),
        ),
        migrations.CreateModel(
            name='HtmlAssetTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField(blank=True)),
                ('caption', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocalDataSet',
            fields=[
                ('dataset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='storybase_asset.DataSet')),
                ('file', filer.fields.file.FilerFileField(to='filer.File', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('storybase_asset.dataset',),
        ),
        migrations.CreateModel(
            name='LocalImageAsset',
            fields=[
                ('asset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='storybase_asset.Asset')),
            ],
            options={
                'abstract': False,
            },
            bases=('storybase_asset.asset',),
        ),
        migrations.CreateModel(
            name='LocalImageAssetTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('title', storybase.fields.ShortTextField(blank=True)),
                ('caption', models.TextField(blank=True)),
                ('asset', models.ForeignKey(related_name='storybase_asset_localimageassettranslation_related', to='storybase_asset.Asset')),
                ('image', filer.fields.image.FilerImageField(to='filer.Image', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='localimageassettranslation',
            unique_together=set([('asset', 'language')]),
        ),
        migrations.AddField(
            model_name='htmlassettranslation',
            name='asset',
            field=models.ForeignKey(related_name='storybase_asset_htmlassettranslation_related', to='storybase_asset.Asset'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='htmlassettranslation',
            unique_together=set([('asset', 'language')]),
        ),
        migrations.AddField(
            model_name='externalassettranslation',
            name='asset',
            field=models.ForeignKey(related_name='storybase_asset_externalassettranslation_related', to='storybase_asset.Asset'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='externalassettranslation',
            unique_together=set([('asset', 'language')]),
        ),
        migrations.AddField(
            model_name='datasettranslation',
            name='dataset',
            field=models.ForeignKey(related_name='storybase_asset_datasettranslation_related', to='storybase_asset.DataSet'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='datasettranslation',
            unique_together=set([('dataset', 'language')]),
        ),
        migrations.AddField(
            model_name='dataset',
            name='owner',
            field=models.ForeignKey(related_name='datasets', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='datasets',
            field=models.ManyToManyField(related_name='assets', to='storybase_asset.DataSet', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='asset',
            name='owner',
            field=models.ForeignKey(related_name='assets', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
