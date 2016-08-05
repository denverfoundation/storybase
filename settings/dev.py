from settings import *

BACKUPDB_DIRECTORY = os.environ['BACKUP_DIR']
MEDIA_ROOT = os.environ['MEDIA_ROOT']
STATIC_ROOT = os.environ['STATIC_ROOT']

DEBUG = True

# Hijack all emails and send them to the BANDIT_EMAIL address
EMAIL_BACKEND = 'bandit.backends.smtp.HijackSMTPBackend'
BANDIT_EMAIL = 'bandit@fusionbox.com'
EMAIL_HOST = 'ASPMX.L.GOOGLE.COM'
EMAIL_PORT = 25
EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL = 'no-reply@floodlightproject.dev'
STORYBASE_CONTACT_EMAIL = "floodlightproject@gmail.com"

# Tell raven to report errors even when debug is True
RAVEN_CONFIG = {
    'register_signals': True,
}

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
TEMPLATES[0]['OPTIONS']['loaders'] = (
    ('django.template.loaders.cached.Loader', TEMPLATES[0]['OPTIONS']['loaders']),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'floodlight',
    }
}

FILER_STORAGES['public']['main']['OPTIONS']['location'] = os.path.abspath(os.path.join(MEDIA_ROOT, 'filer'))
FILER_STORAGES['public']['thumbnails']['OPTIONS']['location'] = os.path.abspath(os.path.join(MEDIA_ROOT, 'filer_thumbnails'))

ALLOWED_HOSTS = [
    'floodlightproject.dev.fusionbox.com',
]

SOCIAL_AUTH_TWITTER_KEY = os.getenv('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.getenv('SOCIAL_AUTH_TWITTER_SECRET')

SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('SOCIAL_AUTH_FACEBOOK_SECRET')
