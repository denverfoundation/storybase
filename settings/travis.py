from defaults import *

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
#        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'atlas_test',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'storybase_geo.search.backends.Solr2155Engine', 
        'URL': 'http://localhost:8080/solr3', 
    },
}
