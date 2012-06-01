import csv

from django.core.management.base import BaseCommand, CommandError

from storybase_user.utils import bulk_create_organization, bulk_create_project

class Command(BaseCommand):
    args = "[csv_file] [type] [name_field] [desc_field]"
    help = ("Load stories from a CSV file\n\n"
            "This is mostly useful for testing\n"
            "Arguments:\n"
            "  csv_file\t\tA CSV file containing information about a project\n"
            "          \t\tor organization\n"
            "  type\t\tThe type of object to create, either 'project' or\n"
            "      \t\torganization\n"
            "  name_field\t\tColumn in CSV file that contains the name\n"
            "  desc_field\t\tColumn in CSV file that contains the description\n")
   
    
    def handle(self, *args, **options):
        try:
            csv_file = open(args[0])
            obj_type = args[1]
            name_field = args[2]
            desc_field = args[3]
        except IndexError:
            raise CommandError("You must provide a CSV file, type, name field "
                               "and description field argument")

        reader = csv.DictReader(csv_file)
        if obj_type == 'organization':
            bulk_create_organization(reader, name_field=name_field,
                                     description_field=desc_field)
        elif obj_type == 'project': 
            bulk_create_project(reader, name_field=name_field,
                                description_field=desc_field)
        else:
            raise CommandError("Object type must be either 'project' or 'organization'")

        csv_file.close()
