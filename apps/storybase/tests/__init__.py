from django.contrib.auth.models import User
from django.test import TestCase

from storybase.models import PermissionMixin

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


class TestPermissionClass(PermissionMixin):
    def user_can_add(self, user):
        return True

    def user_can_delete(self, user):
        return False

    def user_can_change(self, user):
        return True


class PermissionMixinTest(TestCase):
    """Test the PermissionMixin class""" 

    def setUp(self):
        super(PermissionMixinTest, self).setUp()
        self.user = User.objects.create_user("test", "test@example.com", "test")
        self.obj = TestPermissionClass()

    def test_has_perm(self):
        self.assertTrue(self.obj.has_perm(self.user, "add"))
        self.assertFalse(self.obj.has_perm(self.user, "delete"))

    def test_has_perms(self):
        self.assertFalse(self.obj.has_perms(self.user, ["add", "delete"]))
        self.assertTrue(self.obj.has_perms(self.user, ["add", "change"]))

    def test_has_perm_unknown_perm(self):
        self.assertFalse(self.obj.has_perm(self.user, "foo"))
