from settings import *

DEBUG = False

DATABASES = {'default': dj_database_url.config()}

RAVEN_CONFIG = {
    'dsn': 'https://223a9ba8b85b4ba1b5ae2d09831e77e4:8d9c8e76d4854806b3cbf728e2276045@sentry.fusionbox.com/67'
}
