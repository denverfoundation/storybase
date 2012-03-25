from datetime import datetime
from django.test import TestCase

class SloppyTimeTestCase(TestCase):
    """ TestCase with extra assertion methods for checking times """
    def assertNowish(self, timestamp, tolerance=1):
        """ Confirm that a datetime instance is within a few seconds of the current time

        Arguments:
        timestamp -- a datetime.datetime instance
        tolerance -- number of seconds that the times can differ

        """
        delta = datetime.now() - timestamp 
        self.assertTrue(delta.seconds <= tolerance)

    def assertTimesEqualish(self, timestamp1, timestamp2, tolerance=1):
        """ Tests that two datetime instances are within a few seconds of each other

        Arguments:
        timestamp1 -- a datetime.datetime instance
        timestamp2 -- another datetime.datetime instance that must be >= timestamp1
        tolerance -- number of seconds that the times can differ

        """
        delta = timestamp2 - timestamp1
        self.assertTrue(delta.seconds <= tolerance)
