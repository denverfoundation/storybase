from datetime import datetime 

from django.core.mail import get_connection
from django.db import models

class EmailMessageList(list):
    """A list of ``EmailMessage`` objects that can be sent all at once"""

    def send(self):
        """Send all messages in this list"""
        backend = get_connection()
        backend.send_messages(self)


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

        Keyword arguments:

        * send_on - If the notification's ``send_on`` field is equal to or
                    before this field, consider it ready to send.
                    Defaults to ``datetime.now()``.
        """
        qs = self.get_query_set().ready_to_send(send_on)
        qs.emails().send()
        qs.update(sent=datetime.now())
