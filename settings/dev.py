from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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

DEFAULT_FILE_STORAGE =  'django.core.files.storage.FileSystemStorage'
FILER_STORAGES = {
    'public': {
        'main': {
            'ENGINE': DEFAULT_FILE_STORAGE,
            'OPTIONS': {
                'location': os.path.abspath(os.path.join(MEDIA_ROOT, 'filer')),
                'base_url': '/media/filer/',
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.by_date',
            'UPLOAD_TO_PREFIX': '',
        },
        'thumbnails': {
            'ENGINE': DEFAULT_FILE_STORAGE,
            'OPTIONS': {
                'location': os.path.abspath(os.path.join(MEDIA_ROOT, 'filer_thumbnails')),
                'base_url': '/media/filer_thumbnails/',
            },
            'THUMBNAIL_OPTIONS': {
                #'base_dir': 'filer_thumbnails',
                #'base_dir': os.path.abspath(os.path.join(MEDIA_ROOT, 'filer_thumbnails'))
            },
        },
    },
    'private': {
        'main': {
            'ENGINE': 'filer.storage.PrivateFileSystemStorage',
            'OPTIONS': {
                'location': os.path.abspath(os.path.join(MEDIA_ROOT, '../smedia/filer_private')),
                'base_url': '/smedia/filer_private/',
            },
            'UPLOAD_TO': 'filer.utils.generate_filename.by_date',
            'UPLOAD_TO_PREFIX': '',
        },
        'thumbnails': {
            'ENGINE': 'filer.storage.PrivateFileSystemStorage',
            'OPTIONS': {
                'location': os.path.abspath(os.path.join(MEDIA_ROOT, '../smedia/filer_private_thumbnails')),
                'base_url': '/smedia/filer_private_thumbnails/',
            },
            'THUMBNAIL_OPTIONS': {},
        },
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.2:8983/solr/maincore/'
    },
}

BACKUPDB_DIRECTORY = os.environ['BACKUP_DIR']
MEDIA_ROOT = os.environ['MEDIA_ROOT']
STATIC_ROOT = os.environ['STATIC_ROOT']

ALLOWED_HOSTS = [
    'floodlightproject.dev.fusionbox.com',
]
