from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import Context, Template, RequestContext
from django.test import TestCase

from storybase.models import PermissionMixin
from storybase.utils import full_url

class ContextProcessorTest(TestCase):
    def test_conf(self):
        """Test the conf context preprocessor"""
        from django.http import HttpRequest
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
    def setUp(self):
        Site.objects.all().delete()
        self._site_name = "floodlightproject.org"
        self._site_domain = "floodlightproject.org"
        self._site = Site.objects.create(name=self._site_name,
                                         domain=self._site_domain)

    def test_storybase_conf(self):
        """Test the storybase_conf template tag"""
        contact_email = "contactme@example.com"
        settings.STORYBASE_CONTACT_EMAIL = contact_email 
        t = Template("{% load storybase_tags %}{% storybase_conf \"storybase_contact_email\"%}")
        c = Context()
        self.assertEqual(t.render(c), contact_email)

    def test_fullurl(self):
        """Test the fullurl template tag"""
        t = Template("{% load storybase_tags %}{% fullurl \"/stories/asdas/\" %}")
        c = Context()
        self.assertEqual(t.render(c), "http://floodlightproject.org/stories/asdas/")

    def test_fullurl_variable(self):
        """Test the fullurl template tag resolving variable argument"""
        t = Template("{% load storybase_tags %}{% fullurl path %}")
        c = Context({'path': '/stories/asdas/'})
        self.assertEqual(t.render(c), "http://floodlightproject.org/stories/asdas/")

    def test_fullurl_variable_as(self):
        """
        Test the fullurl template tag resolving variable argument and
        saving the result.

        """
        t = Template("{% load storybase_tags %}{% fullurl path as full_path %}")
        c = Context({'path': '/stories/asdas/'})
        t.render(c)
        self.assertEqual(c['full_path'], "http://floodlightproject.org/stories/asdas/")


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


class UtilsTestCase(TestCase):
    """Test for utilities"""
    def setUp(self):
        Site.objects.all().delete()
        self._site_name = "floodlightproject.org"
        self._site_domain = "floodlightproject.org"
        self._site = Site.objects.create(name=self._site_name,
                                         domain=self._site_domain)

    def test_full_url_path(self):
        """Test that a full url is returned when a path is given"""
        path = "/stories/asdas-3/"
        self.assertEqual("http://floodlightproject.org/stories/asdas-3/",
                         full_url(path))

    def test_full_url_path_https(self):
        """
        Test that a full url is returned when a path is given and the 
        scheme is specified.

        """
        path = "/stories/asdas-3/"
        self.assertEqual("https://floodlightproject.org/stories/asdas-3/",
                         full_url(path, 'https'))

    def test_full_url_path_no_proto(self):
        """
        Test that a full url is returned when a blank scheme is specified
        """
        path = "/stories/asdas-3/"
        self.assertEqual("//floodlightproject.org/stories/asdas-3/",
                         full_url(path, None))

    def test_full_url_passthrough(self):
        """
        Test that a full url is just passed through if the argument is
        already a full URL

        """
        path = "http://floodlightproject.org/stories/asdas-3/"
        self.assertEqual("http://floodlightproject.org/stories/asdas-3/",
                         full_url(path))
