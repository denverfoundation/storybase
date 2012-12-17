import hashlib
import os

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test.client import Client

from storybase.tests.base import FileCleanupMixin
from storybase_user.models import ADMIN_GROUP_NAME

class CreateViewTestMixin(FileCleanupMixin):
    def _create_user(self, username, email, password):
        try:
            users = getattr(self, 'users')
        except AttributeError:
            users = self.users = {}

        users[email] = User.objects.create_user(username, email, password)
        return users[email]

    def _get_user(self, email):
        return self.users[email]

    def assertFilesEqual(self, f1, f2):
        hash1 = hashlib.md5(open(f1, 'read').read()).hexdigest()
        hash2 = hashlib.md5(open(f2, 'read').read()).hexdigest()
        self.assertEqual(hash1, hash2)

    def create_model(self, name):
        raise NotImplemented

    def setUp(self):
        super(CreateViewTestMixin, self).setUp()
        self.username = 'test'
        self.password = 'test'
        self.user = self._create_user(self.username, "test@example.com",
                self.password)
        self._create_user("test2", "test2@example.com", "test2")
        self._create_user("test3", "test3@example.com", "test3")
        self.client = Client()

    def test_get_unauthenticated(self):
        """
        Test that the organization creation view cannot be accessed by an
        unauthenticated user
        """
        resp = self.client.get(self.path)
        self.assertEqual(resp.status_code, 302)

    def test_get_authenticated(self):
        """
        Test that the organizaiton creation view can be accessed by an 
        authenticated user
        """
        self.client.login(username=self.username, password=self.password)
        resp = self.client.get(self.path)
        self.assertEqual(resp.status_code, 200)

    def get_default_data(self):
        raise NotImplemented

    def do_test_post(self, extra_data={}, extra_test=None, data=None,
            expect_create=True):
        """
        Do the heavy lifting of POST tests

        This makes the tests more DRY
        """
        if data is None:
            data = self.get_default_data() 
        data.update(extra_data)
        form_id = "create-%s-form" % (self.model._meta.object_name.lower())
        self.assertEqual(self.model.objects.count(), 0)
        self.client.login(username=self.username, password=self.password)
        resp = self.client.post(self.path, data)
        if expect_create:
            # The request should succeed without a redirect
            self.assertEqual(resp.status_code, 200)
            # There shouldn't be a form in the response, because there's
            # a success message
            self.assertNotIn(form_id, resp.content)
            self.assertEqual(self.model.objects.count(), 1)
            obj = self.model.objects.all()[0]
            # The object attributes should match the posted data
            for key in ('name', 'description', 'website_url',):
                val = data[key]
                obj_val = getattr(obj, key)
                self.assertEqual(obj_val, val)
            # The status should be 'pending'
            self.assertEqual(obj.status, 'pending')
            # The owner should match the logged-in user
            through_file_name = self.model._meta.object_name.lower()
            filter_kwargs = {
                through_file_name: obj,
                'member_type': 'owner',
            }
            self.assertEqual(self.model.members.through.objects.filter(
                    **filter_kwargs).count(), 1)
                    
            # The members should have emails that match the posted ones
            self.assertEqual(obj.members.count(), 3)
            for email in ("test2@example.com", "test3@example.com"):
                u = self._get_user(email)
                self.assertIn(u, obj.members.all())

        else:
            self.assertEqual(self.model.objects.count(), 0)
            # There should be a form in the response (to allow correcting
            # the invalid fields
            self.assertIn(form_id, resp.content)
        if extra_test:
            extra_test(resp, obj)

    def test_post(self):
        """
        Test that posting valid data to the organization creation view
        creates a new Organization
        """
        self.do_test_post()

    def test_post_image_file(self):
        """
        Test setting the Organization's image by uploading a file
        """
        image_filename = "test_image.jpg"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "../test_files", image_filename)
        with open(img_path) as fp:
            extra_data = {
                'image_0': fp,
            }
            def extra_test(resp, obj):
                # the featured asset should match the uploaded image
                fa = obj.get_featured_asset()
                self.add_file_to_cleanup(fa.image.file.path)
                self.assertFilesEqual(fa.image.file.path, img_path)
            self.do_test_post(extra_data, extra_test)

    def test_post_image_url(self):
        image_url = 'http://instagr.am/p/BUG/'
        extra_data = {
            'image_1': image_url,
        }
        def extra_test(resp, obj):
            fa = obj.get_featured_asset()
            self.assertEqual(fa.url, image_url)
        self.do_test_post(extra_data, extra_test)

    def test_post_image_malformed_url(self):
        image_url = 'http://asdasd'
        extra_data = {
            'image_1': image_url,
        }
        self.do_test_post(extra_data, expect_create=False)

    def test_post_invalid_no_name(self):
        """
        Test that posting to the organization creation view with a missing
        organization name does not create a new Organization
        """
        data = self.get_default_data()
        del data['name']
        self.do_test_post(data=data, expect_create=False)

    def test_post_invalid_no_description(self):
        """
        Test that posting to the creation view with a missing description
        does not create a new model instance
        """
        data = self.get_default_data()
        del data['description']
        self.do_test_post(data=data, expect_create=False)

    def test_send_create_notification(self):
        backend = getattr(settings, 'EMAIL_BACKEND', None)
        if backend != 'django.core.mail.backends.locmem.EmailBackend':
            self.fail("You must use the in-memory e-mail backend when "
                      "running this test")

        admin_group = Group.objects.create(name=ADMIN_GROUP_NAME)
        admin = User.objects.create(username='admin', 
            password='password', email='admin@example.com')
        admin.groups.add(admin_group)
        view = self.view_class()
        obj = self.create_model(name="Test Organization")
        view.send_create_notification(obj)
        from django.core.mail import outbox
        sent_email = outbox[0]
        self.assertIn(admin.email, sent_email.to)
        self.assertIn(obj.name, sent_email.body)
