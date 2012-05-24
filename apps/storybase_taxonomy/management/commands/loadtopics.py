"""Simple management command for bulk loading topics from CSV"""
import csv

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from storybase_taxonomy.models import Category, CategoryTranslation

class Command(BaseCommand):
    args = "[csv_file] [name_field] [slug_field]"
    help = ("Load place relations from a CSV file\n\n"
            "Arguments:\n"
            "  csv_file\t\tA CSV file containing topics\n"
            "  name_field\t\tName of column in CSV file containing the\n"
            "\t\t\tname of the topic\n"
            "  slug_field\t\tName of column in CSV file containing the\n"
            "\t\t\tthe slug of the topic\n")
    
    def handle(self, *args, **options):
        try:
            csv_file = open(args[0])
            name_field = args[1]
        except IndexError:
            raise CommandError(_("You must provide a CSV file and name "
                                 "field"))

        slug_field = None if len(args) < 3 else args[2]


        reader = csv.DictReader(csv_file)
        for row in reader:
            kwargs = {
                'name': row[name_field]
            }
            if slug_field:
                kwargs['slug'] = row[slug_field]

            category = Category.objects.create();
            kwargs['category'] = category
            CategoryTranslation.objects.create(**kwargs)
            self.stdout.write("Created category %s\n" % (category))

        csv_file.close()
