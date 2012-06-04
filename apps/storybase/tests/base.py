"""TestCase base classes and mixins"""

from datetime import datetime

import django.conf
from django.test import TestCase

class SloppyTimeTestMixin(object):
    """ TestCase with extra assertion methods for checking times """
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
