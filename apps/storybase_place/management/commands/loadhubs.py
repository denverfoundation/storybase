from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from storybase_place.models import Hub, hub_mapping

class Command(BaseCommand):
    args = '<shapefile>'
    help = "Load the Denver Children's Corridor hubs shapefile"

    def handle(self, *args, **options):
        shapefile = args[0]
        print shapefile
        lm = LayerMapping(Hub, shapefile, hub_mapping, transform=True, encoding='iso-8859-1')
        lm.save(strict=True, verbose=True)
