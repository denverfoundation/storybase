from settings import *
"""
To use this, create a `.env` with DJANGO_SETTINGS_MODULE=settings.local
"""

DEBUG = True

DEBUG_TOOLBAR_CONFG = {
    'INTERCEPT_REDIRECTS': False,
}

INSTALLED_APPS.append('debug_toolbar',)

ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SENTRY_DSN = None

COMPRESS_MTIME_DELAY = 0

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
