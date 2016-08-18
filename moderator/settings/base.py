# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use settings_local.py
import os

from django_jinja.builtins import DEFAULT_EXTENSIONS
from django_sha2 import get_password_hashers

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
path = lambda *a: os.path.abspath(os.path.join(ROOT, *a))  # noqa

# Defines the views served for root URLs.
ROOT_URLCONF = 'moderator.urls'
DEBUG = False

INSTALLED_APPS = [
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Third party apps
    'axes',
    'django_browserid',
    'session_csrf',
    # Project specific apps
    'moderator.moderate'
]


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'session_csrf.CsrfMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = path('media')
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = path('static')
STATIC_URL = '/static/'

ADMINS = (
    # ('name', 'email'),
)
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
TIME_ZONE = 'UTC'
# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# Instruct session-csrf to always produce tokens for anonymous users
ANON_ALWAYS = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'moderator.wsgi.application'

CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'session_csrf.context_processor',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'NAME': 'jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'match_extension': '.jinja',
            'newstyle_gettext': True,
            'context_processors': CONTEXT_PROCESSORS,
            'undefined': 'jinja2.Undefined',
            'extensions': DEFAULT_EXTENSIONS,
            'globals': {
                'browserid_info': 'django_browserid.helpers.browserid_info',
                'browserid_login': 'django_browserid.helpers.browserid_login',
                'browserid_logout': 'django_browserid.helpers.browserid_logout',
                'browserid_js': 'django_browserid.helpers.browserid_js'
            }
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': CONTEXT_PROCESSORS
        }
    },
]


def COMPRESS_JINJA2_GET_ENVIRONMENT():
    from django.template import engines
    return engines['jinja2'].env

# Auth
# The first hasher in this list will be used for new passwords.
# Any other hasher in the list can be used for existing passwords.
# To use bcrypt, fill in a secret HMAC key in your local settings.
BASE_PASSWORD_HASHERS = (
    'django_sha2.hashers.BcryptHMACCombinedPasswordVerifier',
    'django_sha2.hashers.SHA512PasswordHasher',
    'django_sha2.hashers.SHA256PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)

HMAC_KEYS = {
    '2015-08-17': 'pancakes',
}

PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)


# Django browserid authentication backend
AUTHENTICATION_BACKENDS = (
    'moderator.moderate.backend.ModeratorBrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SITE_URL = 'https://moderator.mozilla.org'
BROWSERID_AUDIENCES = [SITE_URL]

# Create account for new users.
BROWSERID_CREATE_USER = True
BROWSERID_VERIFY_CLASS = 'moderator.moderate.views.BrowserIDVerify'

# Path to redirect to on successful login.
LOGIN_REDIRECT_URL = '/'
# Path to redirect to on unsuccessful login attempt.
LOGIN_REDIRECT_URL_FAILURE = '/'
LOGOUT_REDIRECT_URL = '/'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Mozillians API
MOZILLIANS_API_BASE = "https://mozillians.org/api/v1/users/"

# Paginator items per page
ITEMS_PER_PAGE = 10

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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
