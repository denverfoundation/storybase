# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def consolidate_locations(apps, schema_editor):
    Place = apps.get_model('storybase_geo', 'Place')
    GeoLevel = apps.get_model('storybase_geo', 'GeoLevel')
    Story = apps.get_model('storybase_story', 'Story')

    try:
        city = GeoLevel.objects.get(slug='city')
    except Exception:
        city = None

    metro_denver, _ = Place.objects.get_or_create(name="Metro Denver",
                                                  slug='metro-denver',
                                                  geolevel=city)
    beyond_metro_denver, _ = Place.objects.get_or_create(name="Colorado — Beyond Metro Denver",
                                                         slug='colorado-beyond-metro-denver')

    try:
        windsor = Place.objects.get(slug='windsor')
    except Exception:
        windsor = None

    for s in Story.objects.all():
        places = [p for p in s.places.all()]
        new_places = []

        if windsor and windsor in places:
            new_places.append(beyond_metro_denver)
            places.remove(windsor)

        if len(places):
            new_places.append(metro_denver)

        if len(new_places):
            s.places.add(*new_places)

    for place in [p for p in Place.objects.all() if p not in (metro_denver, beyond_metro_denver)]:
        place.delete()

def reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('storybase_geo', '0002_auto_20151013_1018'),
    ]

    operations = [
        migrations.RunPython(consolidate_locations, reverse)
    ]
