from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template import Context
from django.template.loader import get_template, TemplateDoesNotExist
from django.utils.translation import get_language, ugettext as _

from storybase.fields import ShortTextField
from storybase.models import (TranslatedModel, TranslationModel,
                              TimestampedModel)
from storybase.utils import full_url
from storybase_messaging.managers import StoryNotificationManager                        
import storybase_messaging.settings as messaging_settings
from storybase_story.models import Story
from storybase_user.utils import send_admin_mail


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
def send_message_to_admins(sender, **kwargs):
    """Send a copy of the message to admins"""
    from django.template.loader import render_to_string 

    instance = kwargs.get('instance')
    subject = _("New message from") + " " + instance.email
    message = render_to_string('storybase_messaging/sitecontactmessage_email.txt',
                               { 'message': instance })
    send_admin_mail(subject, message, instance.email)


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


class StoryNotification(models.Model):
    """
    Notification sent to user on certain story events
    
    This model stores the notification type, story, and date the notification
    should be sent. This allows for using flexible, asynchronous mechanisms
    for sending the notification emails instead of blocking each time the
    story is saved.

    The content for the messages are generated via templates using this naming convention:

    * Message body: ``storybase_messaging/storynotification_NOTIFICATION_TYPE_email__LANGUAGE_CODE.EXTENSION``
      where ``NOTIFICATION_TYPE`` is the value of the ``notification_type``
      field of the model instance, ``LANGUAGE_CODE`` is the language code for
      a particular translation, and ``EXTENSIONS`` is either "txt" or "html"
      depending on whether the message is formatted in plaintext or HTML.
    * Message subject: storybase_messaging/storynotification_NOTIFICATION_TYPE_email_subject__LANGUAGE_CODE.txt

    If translation, is not required or a translation for a particular language
    is not found, these template names will be used:

    * Message body: ``storybase_messaging/storynotification_NOTIFICATION_TYPE_email.EXTENSION``
    * Message subject: ``storybase_messaging/storynotification_NOTIFICATION_TYPE_email_subject.txt``

    """
    NOTIFICATION_TYPES = (
        ('unpublished', 'Reminder of unpublished story'),
        ('published', 'Reminder of published stories'),
    )

    _template_cache = {}

    notification_type = models.CharField(max_length=25, 
        choices=NOTIFICATION_TYPES)
    story = models.ForeignKey(Story)
    sent = models.DateTimeField(blank=True, null=True)
    send_on = models.DateTimeField()

    objects = StoryNotificationManager()

    def get_subject_template_name(self):
        """
        Returns the template name, without filename extension or language
        code for a story notification email's subject
        """
        return "storybase_messaging/storynotification_%s_email_subject" % (self.notification_type)

    def get_template_name(self):
        """
        Returns the template name, without filename extension or language 
        code for a story notification email's body
        """
        return "storybase_messaging/storynotification_%s_email" % (self.notification_type)

    def get_language_choices(self):
        """
        Returns a list of language codes to try when searching for a
        notification message template
        """
        language_code = get_language()
        # First try the active language
        language_choices = [language_code]
        shortened_code = language_code.split('-')[0]
        if shortened_code != language_code:
            # If the active language code specifies a country, e.g. "en-us", 
            # also try the language without the country, e.g. "en"
            language_choices.append(shortened_code)
        if (settings.LANGUAGE_CODE != language_code and 
                settings.LANGUAGE_CODE != shortened_code):
            # Finally, try the default language
            language_choices.append(settings.LANGUAGE_CODE)

        return language_choices

    def get_template(self, template_name_base, content_type="text"):
        """
        Returns a ``Template`` object for the notification message
        
        Keyword arguments:

        content_type - Either "text" or "html".  This determines the
                       extension of the template that will be used.
        """
        extension = ".html" if content_type == "html" else ".txt"
        template = None
        language_choices = self.get_language_choices()
        language_misses = []

        for language in language_choices:
            try:
                template_name = template_name_base + "__" + language + extension
                if template_name in StoryNotification._template_cache:
                    return StoryNotification._template_cache[template_name]
                template = StoryNotification._template_cache[template_name] = get_template(template_name)
            except TemplateDoesNotExist:
                language_misses.append(language)

        template_name = template_name_base + extension

        if template_name in StoryNotification._template_cache:
            return StoryNotification._template_cache[template_name]

        template = StoryNotification._template_cache[template_name] = get_template(template_name)
        for language in language_misses:
            template_name = template_name_base + "__" + language + extension
            StoryNotification._template_cache[template_name] = template 

        return template

    def get_body_template(self, content_type="text"):
        template_name_base = self.get_template_name()
        return self.get_template(template_name_base, content_type)

    def get_subject_template(self):
        template_name_base = self.get_subject_template_name()
        return self.get_template(template_name_base, "text")

    def get_context(self):
        """
        Returns a Context object with elements for the template context of the
        template returned by ``get_template``.
        """
        context = getattr(self, '_context', None)
        if context is not None:
            return context
        else:
            self._context = Context({
              'story': self.story,
              'unpublished_stories': self.story.author.stories.filter(status='draft').exclude(pk=self.story.pk).order_by('-created'),
              'recent_stories': Story.objects.public().exclude(pk=self.story.pk).order_by('-published')[:3],
              # Pre-cook a bunch of URL paths to make template
              # markup leaner
              'viewer_url': full_url(reverse('story_viewer', kwargs={'slug':self.story.slug})),
              'explorer_url': full_url(reverse('explore_stories')),
              'detail_url': full_url(self.story.get_absolute_url()),
            })
            return self._context

    def get_subject(self):
        context = self.get_context()
        template = self.get_subject_template()
        # Strip leading/trailing whitespace from the rendered output, 
        # otherwise there will be an error when sending the EmailMessage
        return template.render(context).strip()

    def get_text_content(self):
        context = self.get_context()
        template = self.get_body_template("text")
        return template.render(context)

    def get_html_content(self):
        context = self.get_context()
        if self.notification_type == "unpublished":
            return None
        else:
            template = self.get_body_template("html")
            return template.render(context)
            
    def get_email(self):
        """
        Returns an ``EmailMultiAlternatives`` object for the story 
        notification message
        """
        subject = self.get_subject()
        from_email = settings.DEFAULT_FROM_EMAIL
        to = self.story.author.email
        text_content = self.get_text_content()
        html_content = self.get_html_content()
        email = EmailMultiAlternatives(subject, text_content, from_email, [to])
        if html_content:
            email.attach_alternative(html_content, "text/html")
        return email 


def update_story_unpublished_notification(sender, instance, **kwargs):
    """Create/update story notification objects based on story state"""
    if instance.status != 'draft':
        return

    profile = instance.author.get_profile()
    if not profile.notify_story_unpublished:
        # The user doesn't want to be notified of unpublished stories
        # so return early
        return

    try:
        notification = StoryNotification.objects.get(notification_type='unpublished', story=instance)
    except StoryNotification.DoesNotExist:
        notification = StoryNotification(notification_type='unpublished',
            story=instance)

    if notification.sent is not None:
        # The notification has already been sent. No need to update it
        return

    # Update the notification to be sent in the future
    days = messaging_settings.STORYBASE_UNPUBLISHED_STORY_NOTIFICATION_DELAY
    delay = timedelta(days=days)
    notification.send_on = datetime.now() + delay 
    notification.save()


def create_story_published_notification(sender, instance, **kwargs):
    StoryNotification.objects.create(notification_type='published',
        story=instance, send_on=datetime.now())
    post_save.disconnect(create_story_published_notification,
        sender=Story,
        dispatch_uid="story_published_notification_%s" % (instance.story_id))


def remove_story_unpublished_notification(sender, instance, **kwargs):
    # Remove any unsent messages
    StoryNotification.objects.filter(story=instance, notification_type='unpublished', sent=None).delete()
    # Disconnect the signal handler
    post_save.disconnect(remove_story_unpublished_notification,
        sender=Story,
        dispatch_uid="remove_story_unpublished_notification_%s" % (instance.story_id))
    

def prepare_story_notification(sender, instance, **kwargs):
    changed_fields = instance.get_dirty_fields().keys()
    if (instance.status == 'published' and instance.pk and 
        'status' in changed_fields):
        # Story was newly published ...
        # Create a notification when it's saved
        post_save.connect(create_story_published_notification,
            sender=Story,
            dispatch_uid="story_published_notification_%s" % (instance.story_id))

        # Remove any "unpublished" notifications
        post_save.connect(remove_story_unpublished_notification,
            sender=Story,
            dispatch_uid="remove_story_unpublished_notification_%s" % (instance.story_id))


post_save.connect(update_story_unpublished_notification, sender=Story)
pre_save.connect(prepare_story_notification, sender=Story)
