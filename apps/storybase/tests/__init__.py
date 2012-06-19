from django.test import TestCase

class ContextProcessorTest(TestCase):
    def test_conf(self):
        """Test the conf context preprocessor"""
        from django.conf import settings
        from django.http import HttpRequest
        from django.template import Template, RequestContext
        from django.contrib.auth.models import AnonymousUser
        contact_email = "contactme@example.com"
        settings.STORYBASE_CONTACT_EMAIL = contact_email 
        t = Template("{{ storybase_contact_email }}")
        user = AnonymousUser()
        req = HttpRequest()
        req.user = user
        c = RequestContext(req)
        self.assertEqual(t.render(c), contact_email)

class TemplateTagTest(TestCase):
    def test_storybase_conf(self):
        """Test the storybase_conf template tag"""
        from django.conf import settings
        from django.template import Context, Template
        contact_email = "contactme@example.com"
        settings.STORYBASE_CONTACT_EMAIL = contact_email 
        t = Template("{% load storybase_tags %}{% storybase_conf \"storybase_contact_email\"%}")
        c = Context()
        self.assertEqual(t.render(c), contact_email)

