import csv

from django.core.management.base import BaseCommand, CommandError

from storybase_story.utils import bulk_create

class Command(BaseCommand):
    args = "[csv_file]"
    help = ("Load stories from a CSV file\n\n"
            "This is mostly useful for testing\n"
            "Arguments:\n"
            "  csv_file\t\tA CSV file containing mappings between places\n")
    
    def handle(self, *args, **options):
        try:
            csv_file = open(args[0])
        except IndexError:
            raise CommandError("You must provide a CSV file argument")

        reader = csv.DictReader(csv_file)
        bulk_create(reader)

        csv_file.close()
