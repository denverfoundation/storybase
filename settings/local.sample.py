from settings import *
"""
To use this, create a `.env` with DJANGO_SETTINGS_MODULE=settings.local
"""

DEBUG = True

INSTALLED_APPS.append('debug_toolbar',)

DEBUG_TOOLBAR_CONFG = {
    'INTERCEPT_REDIRECTS': False,
}
DEBUG_TOOLBAR_PATCH_SETTINGS = False

# FIXME: debug toolbar middleware breaks model translation
# implemented in storybase.models.translation.TranslatedModel
MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware',)

ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SENTRY_DSN = None

COMPRESS_MTIME_DELAY = 0

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
