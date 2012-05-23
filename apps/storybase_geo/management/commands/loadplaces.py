from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from storybase_geo.models import GeoLevel, Place
from storybase_geo.utils.layermapping import ExtraLayerMapping

class Command(BaseCommand):
    args = "<shapefile> <name_field> <boundary_field>"
    help = "Load places from a shapefile"
    option_list = BaseCommand.option_list + (
        make_option('--geolevel',
            action='store',
            dest='geolevel'),
    )

    def handle(self, *args, **options):
        try:
            shapefile = args[0]
            name_field = args[1]
            boundary_field = args[2]
        except IndexError:
            raise CommandError(_("You must provide a shapefile, name "
                                 "field  and boundary field argument"))

        mapping = {'name': name_field,
                   'boundary': boundary_field
                  }
        model_kwargs = {}
        if options['geolevel']:
            model_kwargs['geolevel'] = GeoLevel.objects.get(slug=options['geolevel'])

        lm = ExtraLayerMapping(Place, shapefile, mapping)
        lm.save(verbose=True, model_kwargs=model_kwargs)
