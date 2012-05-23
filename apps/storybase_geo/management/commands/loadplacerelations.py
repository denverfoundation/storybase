import csv

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from storybase_geo.models import GeoLevel, Place, PlaceRelation

class Command(BaseCommand):
    args = "[csv_file] [child_field] [parent_field] [lookup_field] [child_geolevel]"
    help = ("Load place relations from a CSV file\n\n"
            "Arguments:\n"
            "  csv_file\t\tA CSV file containing mappings between places\n"
            "  child_field\t\tName of column in CSV file containing the\n"
            "\t\t\tidentifier for the child place\n"
            "  parent_field\t\tName of column in CSV file containing the\n"
            "\t\t\tidentifier for the parent place\n"
            "  lookup_field\t\tName of model field used to look up places\n"
            "  child_geolevel\tGeoLevel model slug for GeoLevel of\n"
            "\t\t\tchild places\n") 
    
    def handle(self, *args, **options):
        try:
            csv_file = open(args[0])
            child_field = args[1]
            parent_field = args[2]
            lookup_field = args[3]
            child_geolevel = GeoLevel.objects.get(slug=args[4])
        except IndexError:
            raise CommandError(_("You must provide a CSV file, child "
                                 "field, parent field, lookup field and "
                                 "child geolevel argument"))

        reader = csv.DictReader(csv_file)
        try:
            for row in reader:
                child_val = row[child_field]
                parent_val = row[parent_field]
                if child_val and parent_val:
                    child_kwargs = {
                        lookup_field: child_val, 
                        'geolevel': child_geolevel
                    }
                    parent_kwargs = {
                        lookup_field: parent_val, 
                        'geolevel': child_geolevel.parent
                    }
                    try:
                        child = Place.objects.get(**child_kwargs)
                    except Place.DoesNotExist:
                        self.stderr.write("Child Place with %s \"%s\" and "
                            "geolevel \"%s\" does not exist, skipping row\n" %
                            (lookup_field, row[child_field], child_geolevel))
                        continue

                    try:
                        parent = Place.objects.get(**parent_kwargs)
                    except Place.DoesNotExist:
                        self.stderr.write("Parent Place with %s \"%s\" and "
                            "geolevel \"%s\" does not exist, skipping row\n" %
                            (lookup_field, row[parent_field],
                             child_geolevel.parent))
                        continue

                    relation = PlaceRelation(parent=parent, child=child)
                    relation.save()
                    self.stderr.write("Relationship %s created\n" %
                                     (relation))

                else:
                    self.stderr.write("Row has an empty value, skipping\n")

        except IndexError, e:
            raise CommandError(str(e))

        csv_file.close()
