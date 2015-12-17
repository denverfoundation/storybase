from datetime import datetime

from django.core.mail import get_connection
from django.db import models

class EmailMessageList(list):
    """A list of ``EmailMessage`` objects that can be sent all at once"""

    def send(self):
        """
        Send all messages in this list

        Returns a tuple of lists of messages that were successfully sent and
        those that were unsent

        """
        sent = []
        unsent = []
        connection = get_connection()
        connection.open()
        for message in self:
            message.connection = connection
            try:
                message.send()
                sent.append(message)
            except Exception, e:
                # Catch Exception here because the different backends are
                # likely to raise different exception classes
                import logging
                logger = logging.getLogger('storybase')
                recipients = ", ".join(message.to)
                logger.error("Error sending e-mail to %s (%s)" % (recipients, e))
                unsent.append(message)
        connection.close()
        return (sent, unsent)


class StoryNotificationQuerySet(models.query.QuerySet):
    def unsent(self):
        return self.filter(sent=None)

    def ready_to_send(self, send_on=None):
        """
        Returns a queryset filtered to notifications that are ready to send

        Keyword arguments:

        * send_on - If the notification's ``send_on`` field is equal to or
                    before this field, consider it ready to send.
                    Defaults to ``datetime.now()``.

        """
        if send_on is None:
            send_on = datetime.now()

        return self.unsent().filter(send_on__lte=send_on)

    def emails(self):
        emails = EmailMessageList()
        for notification in self:
            emails.append(notification.get_email())
        return emails


class StoryNotificationManager(models.Manager):
    def get_query_set(self):
        return StoryNotificationQuerySet(self.model, using=self._db)

    def send_emails(self, send_on=None):
        """
        Send all notification emails that are ready to send

        Returns a tuple of lists of messages that were successfully sent and
        those that were unsent

        Keyword arguments:

        * send_on - If the notification's ``send_on`` field is equal to or
                    before this field, consider it ready to send.
                    Defaults to ``datetime.now()``.
        """
        qs = self.get_query_set().ready_to_send(send_on)
        (sent, unsent) = qs.emails().send()
        qs.update(sent=datetime.now())
        return (sent, unsent)
