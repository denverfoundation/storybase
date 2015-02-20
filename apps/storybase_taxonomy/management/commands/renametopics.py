"""Command that mass renames topics/tags in the website"""
import csv

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from storybase.utils import slugify, clean_column

import storybase_taxonomy
import storybase_story


class Command(BaseCommand):
    args = "[csv_file]"
    help = ("Mass rename topics from a csv file.\n\n"
            "Arguments:\n"
            "  csv_file\t\tA CSV file containing two columns the name of the\n"
            "  old topic followed by the new topic.")

    def handle(self, *args, **options):

        file_name = args[0]
        csv_file = csv.reader(open(file_name, 'r'))

        print('Skipping headers {}'.format(csv_file.next()))

        data = set()

        for row in csv_file:
            old_topic = clean_column(row[0])
            new_topic = clean_column(row[1])

            if old_topic == new_topic:
                continue

            if old_topic in data:
                raise TypeError("Old topic {} is present twice.".format(old_topic))

            if old_topic is None or new_topic is None:
                raise TypeError(
                    "A topic can't be empty! "
                    "Error while replacing {} with {}.".format(old_topic, new_topic)
                )

            data.add((old_topic, new_topic))

        # here we create the new categories if they don't exist
        storybase_taxonomy.models. \
        create_categories([new_topic_name for (_, new_topic_name) in data])

        stories = storybase_story.models.Story.objects.all()
        renames = 0

        for (old, new) in data:

            new_topic = storybase_taxonomy.models.CategoryTranslation.\
                objects.filter(name=new)[0].category

            old_topic = storybase_taxonomy.models.CategoryTranslation.\
                objects.filter(name=old)[0].category

            for story in stories:
                for topic in story.topics.all():

                    if topic == old_topic:
                        renames += 1

                        print("Replacing {}'s \"{}\" topic with \"{}\"".format(
                            story, topic, new_topic
                        ))

                        story.topics.remove(topic)
                        story.topics.add(new_topic)

                story.save()
        
        print("Done, renamed {} topics".format(renames))
