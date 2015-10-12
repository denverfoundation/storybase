# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import storybase.fields
import mptt.fields
import storybase_geo.models
import django_dag.models
from django.conf import settings
import uuidfield.fields
import storybase.models.dirtyfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', blank=True, to='storybase_geo.GeoLevel', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location_id', uuidfield.fields.UUIDField(auto=True, verbose_name='Location ID', db_index=True)),
                ('name', storybase.fields.ShortTextField(verbose_name='Name', blank=True)),
                ('address', storybase.fields.ShortTextField(verbose_name='Address', blank=True)),
                ('address2', storybase.fields.ShortTextField(verbose_name='Address 2', blank=True)),
                ('city', models.CharField(max_length=255, verbose_name='City', blank=True)),
                ('state', models.CharField(blank=True, max_length=255, verbose_name='State', choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('postcode', models.CharField(max_length=255, verbose_name='Postal Code', blank=True)),
                ('lat', models.FloatField(null=True, verbose_name='Latitude', blank=True)),
                ('lng', models.FloatField(null=True, verbose_name='Longitude', blank=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, verbose_name='Point', blank=True)),
                ('raw', models.TextField(verbose_name='Raw Address', blank=True)),
                ('owner', models.ForeignKey(related_name='locations', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(storybase_geo.models.LocationPermission, storybase.models.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', storybase.fields.ShortTextField(verbose_name='Name')),
                ('boundary', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, verbose_name='Boundary', blank=True)),
                ('place_id', uuidfield.fields.UUIDField(auto=True, verbose_name='Place ID', db_index=True)),
                ('slug', models.SlugField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, django_dag.models.NodeBase),
        ),
        migrations.CreateModel(
            name='PlaceRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child', models.ForeignKey(related_name='place_parent', to='storybase_geo.Place')),
                ('parent', models.ForeignKey(related_name='place_child', to='storybase_geo.Place')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='placerelation',
            unique_together=set([('parent', 'child')]),
        ),
        migrations.AddField(
            model_name='place',
            name='children',
            field=models.ManyToManyField(related_name='_parents', null=True, through='storybase_geo.PlaceRelation', to='storybase_geo.Place', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='geolevel',
            field=models.ForeignKey(related_name='places', verbose_name='GeoLevel', blank=True, to='storybase_geo.GeoLevel', null=True),
            preserve_default=True,
        ),
    ]
