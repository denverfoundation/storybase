from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from storybase_place.models import DenverNeighborhood, denverneighborhood_mapping

class Command(BaseCommand):
    args = '<shapefile>'
    help = 'Load the Denver neighborhood shapefile'

    def handle(self, *args, **options):
        shapefile = args[0]
        print shapefile
        lm = LayerMapping(DenverNeighborhood, shapefile, denverneighborhood_mapping, transform=True, encoding='iso-8859-1')
        lm.save(strict=True, verbose=True)
