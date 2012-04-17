"""Models for the actions app"""

from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string 
from django.utils.translation import ugettext as _

from storybase.fields import ShortTextField
from storybase_user.utils import get_admin_emails

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
    instance = kwargs.get('instance')
    admin_emails = get_admin_emails()
    if admin_emails:
        subject = _("New message from") + " " + instance.email
        message = render_to_string('storybase_action/sitecontactmessage_email.txt',
                                   { 'message': instance })
        send_mail(subject, message, instance.email, admin_emails)
