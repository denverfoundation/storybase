from datetime import datetime
import logging
from optparse import make_option

from django.core.management.base import BaseCommand

logger = logging.getLogger('storybase.messaging.management')

class Command(BaseCommand):
    help = ("Send story notification emails whose send on date/time is now\n"
            "or in the past\n\n"
            "This is intended to be run from a cron job.\n\n"
            )
    option_list = BaseCommand.option_list + (
            make_option('--send-on',
                action='store',
                dest='send_on',
                default=None,
                help="Specify a send on date/time other than now"),
            )

    def handle(self, *args, **options):
        try:
            send_on = options.get('send_on', None)
            if send_on is not None:
                # If specified, convert the send_on option from a string
                # to a datetime object
                send_on = datetime.strptime(send_on)

            from storybase_messaging.models import StoryNotification
            (sent, unsent) = StoryNotification.objects.send_emails(send_on=send_on)

            message = "%d story notifications sent" % (len(sent))
            if len(unsent):
                message += " %d story notifications failed" % (len(unsent))

            logger.info(message)
            if int(options.get('verbosity')) > 1:
                self.stdout.write(message + "\n")
        except Exception, e:
            message = "Uncaught exception when sending story notifications: %s" % (e)
            logger.error(message)
            self.stdout.write(message)
