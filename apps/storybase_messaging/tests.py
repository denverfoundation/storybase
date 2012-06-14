"""Tests for the actions app"""

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase

from storybase_user.models import ADMIN_GROUP_NAME
from storybase_messaging.models import SiteContactMessage

class SiteContactMessageModelTest(TestCase):
    """Test methods of the SiteContactMessge model"""
    def test_email_sent_on_save(self):
        """
        Tests that an email is sent when a message is saved. 
        """
        backend = getattr(settings, 'EMAIL_BACKEND', None)
        if backend != 'django.core.mail.backends.locmem.EmailBackend':
            self.fail("You must use the in-memory e-mail backend when "
                      "running this test")

        name = 'Jane Doe'
        email = 'jane@doe.com'
        phone = '123-456-7890'
        message_body = ("I am interested in your site.\n"
                        "Please give me more information\n"
                        "\n"
                        "Thanks,\n"
                        "Jane")
        admin_group = Group.objects.create(name=ADMIN_GROUP_NAME)
        admin = User.objects.create(username='admin', 
            password='password', email='admin@example.com')
        admin.groups.add(admin_group)
        admin.save()
        SiteContactMessage.objects.create(name=name, email=email,
            phone=phone, message=message_body)
            
        from django.core.mail import outbox
        sent_email = outbox[0]
        self.assertEqual(sent_email.from_email, email)
        self.assertEqual(sent_email.subject, 
                         "New message from %s" % email)
        self.assertIn(admin.email, sent_email.to)
        self.assertIn(name, sent_email.body)
        self.assertIn(phone, sent_email.body)
        self.assertIn(message_body, sent_email.body)
