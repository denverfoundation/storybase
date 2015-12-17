import json
import sys
from urlparse import parse_qs

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files import File
from django.core.serializers.json import DjangoJSONEncoder
from django.template import Context, Template, RequestContext
from django.test import TestCase

from storybase.models import PermissionMixin
from storybase.forms import UserEmailField
from storybase.tests.base import SettingsChangingTestCase
from storybase.utils import (escape_json_for_html, full_url,
    get_language_name, is_file)

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


class FilterTest(TestCase):
    def test_classname(self):
        """Test the classname filter"""
        class MockClass(object):
            pass
        t = Template("{% load storybase_tags %}{{ object|classname }}")
        c = Context({'object': MockClass(),})
        output = "MockClass"
        self.assertEqual(t.render(c), output)


    def test_camelsplit(self):
        t = Template("{% load storybase_tags %}{{ s|camelsplit|first }}")
        c = Context({'s': "UserProfile"})
        output = "User"
        self.assertEqual(t.render(c), output)


class TemplateTagTest(SettingsChangingTestCase):
    def setUp(self):
        super(TemplateTagTest, self).setUp()
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

    def test_ga_campaign_params(self):
        self.set_setting('GA_PROPERTY_ID', 'UA-11111111-1')
        t = Template('{% load storybase_tags %}{% ga_campaign_params "exampleblog" "referral" "spring" %}')
        c = Context()
        params = parse_qs(t.render(c).lstrip('?'))
        self.assertEqual(params['utm_source'][0], 'exampleblog')
        self.assertEqual(params['utm_medium'][0], 'referral')
        self.assertEqual(params['utm_campaign'][0], 'spring')


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


class UserEmailFieldTest(TestCase):
    """Tests for UserEmailField form field"""
    def test_split(self):
        f = UserEmailField(required=False)
        emails = ["test@example.com", "test2@example.com",
                "test3@example.com", "test4@example.com", "test5@example.com"]
        split_values = f.split_value("test@example.com, test2@example.com,test3@example.com,test4@example.com,\t\t\ntest5@example.com")
        self.assertEqual(split_values, emails)

    def test_clean(self):
        u1 = User.objects.create_user("test", "test@example.com", "test")
        u2 = User.objects.create_user("test2", "test2@example.com", "test2")
        u3 = User.objects.create_user("test3", "test3@example.com", "test3")
        f = UserEmailField(required=False)
        users = f.clean("test@example.com, test2@example.com,test3@example.com,test4@example.com,\t\t\ntest5@example.com,sdadssafasfas")
        self.assertEqual(len(users), 3)
        self.assertIn(u1, users)
        self.assertIn(u2, users)
        self.assertIn(u3, users)


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

    def test_is_file_true(self):
        f = File(sys.stdout)
        self.assertTrue(is_file(f))

    def test_is_file_false(self):
        s = u"This is a string, not a file"
        self.assertFalse(is_file(s))

    def test_escape_json_for_html(self):
        data = {
            'title': "Test Title",
            'body': "<script src=\"http://floodlightproject.org/fake.js\"></script>",
        }

        json_str = json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True, ensure_ascii=False)
        escaped_json_str = escape_json_for_html(json_str)
        self.assertEqual(json.loads(json_str)['body'],
                         json.loads(escaped_json_str)['body'])

    def test_get_language_name(self):
        self.assertEqual("English", get_language_name("en"))
