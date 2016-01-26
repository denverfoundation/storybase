# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def add_locations(apps, schema_editor):
    Place = apps.get_model('storybase_geo', 'Place')

    places = (
        "Beyond Colorado",
        "Adams County",
        "Arapahoe County",
        "Boulder County",
        "Broomfield County",
        "Denver - Far Northeast",
        "Denver - Northeast",
        "Denver - Northwest",
        "Denver - Southeast",
        "Denver - Southwest",
        "Douglas County",
        "Jefferson County",
    )
    for p in places:
        Place.objects.get_or_create(name=p)

def reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('storybase_geo', '0003_consolidate_locations'),
    ]

    operations = [
        migrations.RunPython(add_locations, reverse)
    ]
