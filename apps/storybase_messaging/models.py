from django.conf import settings
from django.db import models

from storybase.fields import ShortTextField
from storybase.models import (DirtyFieldsMixin,
                              TranslatedModel, TranslationModel,
                              TimestampedModel)
if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class MessageTranslation(TranslationModel):
    subject = ShortTextField() 
    body = models.TextField()

    class Meta:
        abstract = True


class Message(TranslatedModel, TimestampedModel, DirtyFieldsMixin):
    sent = models.DateTimeField(blank=True, null=True)

    translated_fields = ['subject', 'body']

    class Meta:
        abstract = True


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
