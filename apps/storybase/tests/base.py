"""TestCase base classes and mixins"""

from datetime import datetime
from urlparse import urlparse

import django.conf
from django.test import TestCase
from django.test.client import FakePayload

from tastypie.test import TestApiClient

class FileCleanupMixin(object):
    """Delete files created during tests"""
    def setUp(self):
        super(FileCleanupMixin, self).setUp()
        self._files_to_cleanup = []

    def add_file_to_cleanup(self, path):
        self._files_to_cleanup.append(path)

    def cleanup_files(self):
        import os
        for path in self._files_to_cleanup:
            os.remove(path)

    def tearDown(self):
        super(FileCleanupMixin, self).tearDown()
        self.cleanup_files()


class SloppyComparisonTestMixin(object):
    """Extra assertion methods for checking times"""
    def assertNowish(self, timestamp, tolerance=1):
        """ Confirm datetime instance is close to current time

        Arguments:
        timestamp -- a datetime.datetime instance
        tolerance -- number of seconds that the times can differ

        """
        delta = datetime.now() - timestamp 
        self.assertTrue(delta.seconds <= tolerance)

    def assertTimesEqualish(self, timestamp1, timestamp2, tolerance=1):
        """ Confirm two datetime instances are close to one another

        Arguments:
        timestamp1 -- a datetime.datetime instance
        timestamp2 -- another datetime.datetime instance that must be >= timestamp1
        tolerance -- number of seconds that the times can differ

        """
        delta = timestamp2 - timestamp1
        self.assertTrue(delta.seconds <= tolerance)

    def assertApxEqual(self, value1, value2, precision=1e-03):
        """Tests that values are approximately equal to each other"""
        if (not (abs(value1 - value2) <= precision)):
            self.fail("abs(%f - %f) is not less than %f" %
                      (value1, value2, precision))



class SettingsChangingTestCase(TestCase):
    """TestCase that allows for changing (and then restoring) settings"""
    def get_settings_module(self):
        from django.conf import settings
        return settings

    def setUp(self, settings_module=django.conf.settings):
        self._settings_module=settings_module
        self._old_settings = {}

    def tearDown(self):
        settings_module = self.get_settings_module()
        for key, value in self._old_settings.items():
            setattr(settings_module, key, value)

class FixedTestApiClient(TestApiClient):
    """
    Version of TestApiClient that fixes the patch() method

    See https://github.com/toastdriven/django-tastypie/issues/531
    
    """
    def patch(self, uri, format='json', data=None, authentication=None, **kwargs):
        """
        Performs a simulated ``PATCH`` request to the provided URI.

        Optionally accepts a ``data`` kwarg. **Unlike** ``GET``, in ``PATCH`` the
        ``data`` gets serialized & sent as the body instead of becoming part of the URI.
        Example::

            from tastypie.test import TestApiClient
            client = TestApiClient()

            response = client.patch('/api/v1/entry/1/', data={
                'created': '2012-05-01T20:02:36',
                'slug': 'another-post',
                'title': 'Another Post',
                'user': '/api/v1/user/1/',
            })

        Optionally accepts an ``authentication`` kwarg, which should be an HTTP header
        with the correct authentication data already setup.

        All other ``**kwargs`` passed in get passed through to the Django
        ``TestClient``. See https://docs.djangoproject.com/en/dev/topics/testing/#module-django.test.client
        for details.
        """
        content_type = self.get_content_type(format)
        kwargs['content_type'] = content_type

        if data is not None:
            # Convert serializer output to a string because FakePayload doesn't handle unicode
            kwargs['data'] = str(self.serializer.serialize(data, format=content_type))

        if authentication is not None:
            kwargs['HTTP_AUTHORIZATION'] = authentication

        # This hurts because Django doesn't support PATCH natively.
        parsed = urlparse(uri)
        r = {
            'CONTENT_LENGTH': len(kwargs['data']),
            'CONTENT_TYPE': content_type,
            'PATH_INFO': self.client._get_path(parsed),
            'QUERY_STRING': parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input': FakePayload(kwargs['data']),
        }
        r.update(kwargs)
        return self.client.request(**r)

