from defaults import *

DEBUG=False

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
#        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'atlas_travis',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Haystack doesn't correctly hook up RealTimeIndex signals when
# migrations are enabled, so disable migrations.
# See https://github.com/toastdriven/django-haystack/issues/599
SOUTH_TESTS_MIGRATE = False

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'storybase_geo.search.backends.Solr2155Engine', 
        'URL': 'http://localhost:8080/solr3', 
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
