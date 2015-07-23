import dj_database_url
import os

from decouple import Csv, config

DEBUG = config('DEBUG', cast=bool)
TEMPLATE_DEBUG = config('TEMPLATE_DEBUG', default=DEBUG, cast=bool)

DATABASES = {
    'default': config('DATABASE_URL', cast=dj_database_url.parse)
}

CACHES = {
    'default': {
        'BACKEND': config('CACHE_BACKEND', default='django.core.cache.backends.locmem.LocMemCache'),  # noqa
        'LOCATION': config('CACHE_LOCATION', default='unique-snowflake')
    }
}

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

TIME_ZONE = config('TIME_ZONE', default='UTC')
LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')
USE_I18N = config('USE_I18N', default=True, cast=bool)
USE_L10N = config('USE_L10N', default=True, cast=bool)
USE_TZ = config('USE_TZ', default=True, cast=bool)

PROJECT_DIR = os.path.dirname(__file__)
MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(PROJECT_DIR, 'media'))
MEDIA_URL = config('MEDIA_URL', default='/media/')

STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(PROJECT_DIR, 'static'))  # noqa
STATIC_URL = config('STATIC_URL', default='/static/')

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(PROJECT_DIR, 'moderate/static'),)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = config('SECRET_KEY')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

JINGO_EXCLUDE_APPS = ('admin', 'browserid',)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'axes.middleware.FailedLoginMiddleware',
)

ROOT_URLCONF = 'moderator.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'moderator.wsgi.application'

TEMPLATE_DIRS = (
    'templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django_browserid',

    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'south',
    'axes',
    'moderator.moderate',
)

# Django browserid authentication backend
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'moderator.moderate.backend.ModeratorBrowserIDBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages')

SITE_URL = config('SITE_URL')

BROWSERID_AUDIENCES = [SITE_URL]
BROWSERID_CREATE_USER = True

LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = '/'
LOGOUT_REDIRECT_URL = '/'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

BROWSERID_VERIFY_CLASS = 'moderator.moderate.views.BrowserIDVerify'
MOZILLIANS_API_BASE = "https://mozillians.org/api/v1/users/"
MOZILLIANS_API_KEY = config('MOZILLIANS_API_KEY')
MOZILLIANS_API_APPNAME = config('MOZILLIANS_API_APPNAME')
ITEMS_PER_PAGE = 10
