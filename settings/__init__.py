import os
import sys

import dj_database_url

# Dummy Gettext
ugettext = lambda s: s

PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Add apps directory to PYTHONPATH so I can refer to apps as if they were
# reusable
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))

# Production installs need to have this environment variable set
DEFAULT_SECRET_KEY = 'SECRET_KEY'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', DEFAULT_SECRET_KEY)

ADMINS = (
    ('Programmers', 'programmers@fusionbox.com'),
)

MANAGERS = ADMINS

# DEBUG based settings.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('t', 'true', 'y', 'yes', '1')

DATABASES = {'default': dj_database_url.config(default='sqlite:///sqlite_database')}
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASE_ENGINE = DATABASES['default']['ENGINE']

INTERNAL_IPS = (
    '127.0.0.1',
    '208.186.116.206',
    '208.186.142.130',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Tell raven to report errors even when debug is True
RAVEN_CONFIG = {
    'register_signals': True,
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Denver'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Search for translations in the project-wide locale folder
LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, 'locale'),
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, "sitestatic")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, "static2"),
    os.path.join(PROJECT_PATH, "static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'media_staticfiles_finder.AppDirectoriesFinderAsMedia',
    'compressor.finders.CompressorFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    # If not using Django CMS, or some other app that has
    # a "catch-all" url regex, just use
    # 'django.middleware.locale.LocaleMiddleware',
    'storybase.middleware.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # django CMS middleware
    'cms.middleware.language.LanguageCookieMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',

    'storybase.middleware.ExtractContentMiddleware',
]

# This prevents clickjacking <http://en.wikipedia.org/wiki/Clickjacking>
X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'
FORCE_SCRIPT_NAME = ''

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, "templates2"),
    os.path.join(PROJECT_PATH, "templates")
)

CMS_TEMPLATES = (
    ('homepage.html', 'Home Page'),
    ('cms_twocol.html', 'Two Column'),
    ('faq.html', 'FAQ'),
    ('cms_section_landing.html', 'Section Landing'),
    ('activity_guides.html', 'Activity Guides'),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.gis',
    'localflavor',

    'raven.contrib.django',
    'bandit',
    'backupdb',

    # django CMS requirements
    'cms',
    'easy_thumbnails',
    'filer',
    'mptt',
    'menus',
    'reversion',
    'south',
    'sekizai',

    # django CMS plugins
    'cms.plugins.text',
    'cmsplugin_filer_file',
    'cmsplugin_filer_folder',
    'cmsplugin_filer_image',
    'cmsplugin_filer_teaser',
    'cmsplugin_filer_video',

    # StoryBase dependencies
    #'ajax_select',
    'haystack',
    'taggit',
    'tastypie',
    'categories.editor',
    'tinymce',
    'registration',
    'social_auth',
    'django.contrib.comments',
    'threadedcomments',
    'notification',
    'compressor',

    # StoryBase
    'storybase',
    'storybase_help',
    'storybase_badge',
    'storybase_user',
    'storybase_asset',
    'storybase_story',
    'storybase_taxonomy',
    'storybase_geo',
    'storybase_messaging',
    'cmsplugin_storybase',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
    'social_auth.context_processors.social_auth_by_name_backends',
    'storybase.context_processors.conf',
    'storybase.context_processors.site',
)

AUTH_PROFILE_MODULE = 'storybase_user.UserProfile'

LOGIN_REDIRECT_URL = '/accounts/stories/'
LOGOUT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'storybase_user.auth.backends.EmailModelBackend',
    # Allow lookup by username, but try email address first
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'storybase_user.social_auth.pipeline.redirect_to_form',
    'storybase_user.social_auth.pipeline.get_data_from_user',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
)
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/accounts/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/accounts/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'default',
        },
        'mail_admins': {
            'level': 'INFO',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'storybase': {
            'handlers': ['null'],
            'level': 'INFO',
            'propogate': True,
        },
        'storybase_user.admin': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'propogate': True,
        },
    }
}

LANGUAGES = [
    ('en', ugettext('English')),
    ('es', ugettext('Spanish')),
]

# Don't hide menu items that are untranslated
CMS_HIDE_UNTRANSLATED = False

# Allow overriding menu titles
CMS_MENU_TITLE_OVERWRITE = True

TAGGIT_AUTOSUGGEST_MODEL = 'storybase_tag.models.Tag'

FILER_STATICMEDIA_PREFIX = os.path.join(STATIC_URL, 'filer/')

# define the lookup channels for use with ajax_select
AJAX_LOOKUP_CHANNELS = {
    'asset': {'model': 'storybase_asset.asset', 'search_field': 'title'},
}
# magically include jqueryUI/js/css
AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'inline'

# tinymce settings
TINYMCE_JS_URL = os.path.join(STATIC_URL, 'js/libs/tiny_mce/tiny_mce.js')
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, 'js/libs/tiny_mce')

# registration settings
ACCOUNT_ACTIVATION_DAYS = 7

# commenting settings
COMMENTS_APP = 'threadedcomments'

THUMBNAIL_PROCESSORS = (
    # This is needed for cmsplugin_filer_image to work correctly
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
)

# Always create thumbnails as the same type as the original
THUMBNAIL_PRESERVE_EXTENSIONS = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'storybase_geo.search.backends.Solr2155Engine',
        'URL': 'http://localhost:8983/solr/floodlight_dev',
        'INCLUDE_SPELLING': True,
    },
}

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

# This often breaks the system because of a circular import - this may be required
#
# HAYSTACK_SIGNAL_PROCESSOR = 'storybase.search.signals.RealtimeSignalProcessor'

# storybase settings
# The name of the group used for site administrators
ADMIN_GROUP_NAME = 'CA Admin'
# The "from" address of emails sent from the system
# Set this in per-instance settings
#DEFAULT_FROM_EMAIL = ''
# The name of the site
STORYBASE_SITE_NAME = "Your Storybase Site"
STORYBASE_SITE_DESCRIPTION = ugettext("A powerful story-building website that enables community change makers to inspire action and advance their issues through more substantive, engaging and persuasive data-driven storytelling.")
# The tagline of the site
STORYBASE_SITE_TAGLINE = ugettext("Your site tagline")
# The title of the organization list view
STORYBASE_ORGANIZATION_LIST_TITLE = ugettext("Organizations")
# The title of the project list view
STORYBASE_PROJECT_LIST_TITLE = ugettext("Projects")
# The title of the story exploration view
STORYBASE_EXPLORE_TITLE = ugettext("Explore")
# A tuple representing the latitude and longitude of where the story
# exploration map should be centered
STORYBASE_MAP_CENTER = (39.74151, -104.98672)
# Initial map zoom level
STORYBASE_MAP_ZOOM_LEVEL = 11
# Distance in miles to search around a point when doing a proximity search
STORYBASE_SEARCH_DISTANCE = 1
# Zoom level when zooming into a point
STORYBASE_MAP_POINT_ZOOM_LEVEL = 14
STORYBASE_CONTACT_EMAIL = ""
# Layout templates
STORYBASE_LAYOUT_TEMPLATES = (
    'side_by_side.html',
    '1_up.html',
    'above_below.html',
    '3_stacked.html',
)
# Connected story template slug
STORYBASE_CONNECTED_STORY_TEMPLATE = "connected"

# Default images
STORYBASE_DEFAULT_ORGANIZATION_IMAGES = {
    100: STATIC_URL + 'img/default-image-organization-100x60.png',
    150: STATIC_URL + 'img/default-image-organization-150x90.png',
    222: STATIC_URL + 'img/default-image-organization-222x132.png',
    335: STATIC_URL + 'img/default-image-organization-335x200.png',
}
STORYBASE_DEFAULT_PROJECT_IMAGES = {
    100: STATIC_URL + 'img/default-image-project-100x60.png',
    150: STATIC_URL + 'img/default-image-project-150x90.png',
    222: STATIC_URL + 'img/default-image-project-222x132.png',
    335: STATIC_URL + 'img/default-image-project-335x200.png',
}
STORYBASE_DEFAULT_STORY_IMAGES = {
    100: STATIC_URL + 'img/default-image-story-100x60.png',
    150: STATIC_URL + 'img/default-image-story-150x90.png',
    222: STATIC_URL + 'img/default-image-story-222x132.png',
    335: STATIC_URL + 'img/default-image-story-335x200.png',
}
STORYBASE_DEFAULT_USER_IMAGES = {
    100: STATIC_URL + 'img/default-image-user-100x60.png',
    150: STATIC_URL + 'img/default-image-user-150x90.png',
    222: STATIC_URL + 'img/default-image-user-222x132.png',
    335: STATIC_URL + 'img/default-image-user-335x200.png',
}

# Browser support message that will be shown if a user's browser lacks
# support for certain features required by the site.
STORYBASE_BROWSER_SUPPORT_MSG = "This site works best in a recent version of <a href='http://www.mozilla.org/firefox/' title='Mozilla Firefox'>Firefox</a> or <a href='http://www.google.com/chrome/' title='Google Chrome'>Chrome</a>. If you are using an older browser, we recommend updating to the latest version."

# Allowed HTML tags in user-submitted content. Note that restrictions for
# asset content is a little looser.  These apply to things like story
# summaries and call to actions
STORYBASE_ALLOWED_TAGS = [
  'a',
  'abbr',
  'b',
  'blockquote',
  'br',
  'cite',
  'code',
  'div',
  'em',
  'h3',
  'i',
  'li',
  'ol',
  'p',
  'span',
  'strong',
  'u',
  'ul',
]

# Should we use LESS stylesheets in the browser and compile them using less.js
# It would be easy to just toggle this using the DEBUG setting, but IE8
# isn't supported by less.js and we need to be able to quickly test out
# stylesheet fixes with the development server.
STORYBASE_USE_LESS_IN_BROWSER = False

# Attempt to configure sentry from an environment variable.
try:
    SENTRY_DSN = os.environ['SENTRY_DSN']
except KeyError:
    pass
