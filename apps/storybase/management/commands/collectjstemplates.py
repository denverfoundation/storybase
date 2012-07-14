import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = ""
    help = "Collect Javascript templates in a place where they're available to Jasmine tests"

    destination_dir = os.path.join(settings.PROJECT_PATH, 'static/js/spec/fixtures/')

    def get_template_files(self):
        def add_project_root(path):
            return os.path.join(settings.PROJECT_PATH, path) 

        template_files = (
            "apps/storybase_story/templates/storybase_story/story_builder_handlebars.html",
        )

        return map(add_project_root, template_files)

    def handle(self, *args, **options):
        for template_file in self.get_template_files():
            self.stderr.write("Copying %s to %s\n" % (template_file, self.destination_dir))
            shutil.copy(template_file, self.destination_dir)
