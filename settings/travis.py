from defaults import *

DEBUG=False

SECRET_KEY='+9*_1$hry$2r5#723%_a@uju&-skn)^042r+d_eupq*az8o^(w'

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
        'URL': 'http://localhost:8983/solr/travis',
        # If the Solr/Jetty install on Travis CI is broken, use the
        # mock backend which will cause some tests to be skipped
        #'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
