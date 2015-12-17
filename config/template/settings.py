from defaults import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '%(db_name)s',
        'USER': '%(db_username)s',
        'PASSWORD': '%(db_password)s',
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

HAYSTACK_SOLR_URL = 'http://127.0.0.1:8080/solr'

