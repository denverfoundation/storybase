from defaults import *

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'atlas_test',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# These settings are required the create a spatial database when 
# testing GeoDjango apps.
# See http://geodjango.org/docs/testing.html?highlight=testing#testing-geodjango-apps
TEST_RUNNER='django.contrib.gis.tests.run_tests'
POSTGIS_TEMPLATE='template_postgis'
