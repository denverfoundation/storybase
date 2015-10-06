from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
DEBUG_TOOLBAR_PATCH_SETTINGS = False

# Hijack all emails and send them to the BANDIT_EMAIL address
EMAIL_BACKEND = 'bandit.backends.smtp.HijackSMTPBackend'
BANDIT_EMAIL = 'plee@fusionbox.com'
EMAIL_HOST = 'ASPMX.L.GOOGLE.COM'
EMAIL_PORT = 25
EMAIL_USE_TLS = False

# Tell raven to report errors even when debug is True
RAVEN_CONFIG = {
    'register_signals': True,
}

TEMPLATE_LOADERS = (
    ('django.template.loders.cached.loader', TEMPLATE_LOADERS),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'floodlight',
    }
}

# TODO: HAYSTACK_CONNECTIONS

BACKUPDB_DIRECTORY = os.environ['BACKUP_DIR']
MEDIA_ROOT = os.environ['MEDIA_ROOT']
STATIC_ROOT = os.environ['STATIC_ROOT']

ALLOWED_HOSTS = [
    'floodlightproject.dev.fusionbox.com',
    'localhost',
]
