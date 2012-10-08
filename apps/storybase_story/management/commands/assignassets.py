from optparse import make_option

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

class Command(BaseCommand):
    args = "[slug_or_id]"
    help = ("Assign all assets assigned to sections to the story\n\n"
            "This is a fix for the case where some stories edited in the\n"
            "Django admin had their assets assigned to the section, but\n"
            "not the story\n\n"
            "Arguments:\n"
            "  slug_or_id\t\tA story slug or ID\n")
    option_list = BaseCommand.option_list + (
            make_option('--dry-run',
                action='store_true',
                dest='dry_run',
                default=False,
                help="Show assets that would be added, but don't add them"),
            )

    
    def handle(self, *args, **options):
        # Import here to prevent some weird circular import
        from storybase_story.models import Story, SectionAsset

        try:
            slug_or_id = args[0] 
            q = Q(story_id=slug_or_id)
            q = q | Q(slug=slug_or_id)
            story = Story.objects.get(q)
            changed = False
            for sa in SectionAsset.objects.filter(section__story=story):
                if sa.asset not in story.assets.all():
                    changed = True
                    self.stdout.write('Adding asset "%s"' % sa.asset)
                    if not options['dry_run']:
                        story.assets.add(sa.asset)
            if changed and not options['dry_run']:
                story.save()

        except ObjectDoesNotExist:
            raise CommandError('A story matching "%s" could not be found' %
                slug_or_id)
        except IndexError:
            raise CommandError("You must provide a story slug or ID as "
                               "an argument")
