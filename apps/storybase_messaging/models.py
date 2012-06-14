from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from storybase.fields import ShortTextField
from storybase.models import (TranslatedModel, TranslationModel,
                              TimestampedModel)
from storybase_user.utils import get_admin_emails


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class MessageTranslation(TranslationModel):
    subject = ShortTextField() 
    body = models.TextField()

    class Meta:
        abstract = True


class Message(TranslatedModel, TimestampedModel):
    sent = models.DateTimeField(blank=True, null=True)

    translated_fields = ['subject', 'body']

    class Meta:
        abstract = True


class SiteContactMessage(models.Model):
    """A message to the site administrators"""
    name = ShortTextField(_("Your Name"))
    email = models.EmailField(_("Your Email"))
    phone = models.CharField(_("Your Phone Number"), max_length=20,
                             blank=True)
    message = models.TextField(_("Your Message"))
    created = models.DateTimeField(_("Message Created"), auto_now_add=True)

    def __unicode__(self):
        return unicode(_("Message from ") + self.email)


@receiver(post_save, sender=SiteContactMessage)
def send_email_to_admins(sender, **kwargs):
    """Send a copy of the message to admins"""
    from django.template.loader import render_to_string 
    from django.core.mail import send_mail

    instance = kwargs.get('instance')
    admin_emails = get_admin_emails()
    if admin_emails:
        subject = _("New message from") + " " + instance.email
        message = render_to_string('storybase_messaging/sitecontactmessage_email.txt',
                                   { 'message': instance })
        send_mail(subject, message, instance.email, admin_emails)


class SystemMessageTranslation(MessageTranslation):
    message = models.ForeignKey('SystemMessage')


class SystemMessage(Message):
    translation_set = 'systemmessagetranslation_set'

    notification_type = "system_message"

    def send_notifications(self):
        """Send a notification to all users"""
        from datetime import datetime
        if notification:
            from django.contrib.auth.models import User

            context = {
                'message': self,
            }
            notification.send(User.objects.filter(is_active=True), 
                              self.notification_type, 
                              context, on_site=False, queue=True)
        else:
            pass

        self.sent = datetime.now()
        self.save()
