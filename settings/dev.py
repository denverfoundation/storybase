from settings import *

BACKUPDB_DIRECTORY = os.environ['BACKUP_DIR']
MEDIA_ROOT = os.environ['MEDIA_ROOT']
STATIC_ROOT = os.environ['STATIC_ROOT']

DEBUG = True

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

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.2:8983/solr/maincore/'
    },
}

ALLOWED_HOSTS = [
    'floodlightproject.dev.fusionbox.com',
]
