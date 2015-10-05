from __future__ import absolute_import

from .settings import *

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SENTRY_DSN = None

INSTALLED_APPS.append('debug_toolbar')

COMPRESS_MTIME_DELAY = 0
