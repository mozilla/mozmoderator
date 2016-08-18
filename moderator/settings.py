# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use local.py
import json
import os

import dj_database_url
from decouple import Csv, config
from django_jinja.builtins import DEFAULT_EXTENSIONS
from django_sha2 import get_password_hashers

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
path = lambda *a: os.path.abspath(os.path.join(ROOT, *a))  # noqa

# Defines the views served for root URLs.
ROOT_URLCONF = 'moderator.urls'

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

SITE_ID = 1

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

# Django browserid authentication backend
AUTHENTICATION_BACKENDS = (
    'moderator.moderate.backend.ModeratorBrowserIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

HMAC_KEYS = config('HMAC_KEYS', cast=json.loads)

PASSWORD_HASHERS = get_password_hashers(BASE_PASSWORD_HASHERS, HMAC_KEYS)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


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

# Internationalization
TIME_ZONE = config('TIME_ZONE', default='UTC')
USE_I18N = config('USE_I18N', default=False, cast=bool)
USE_L10N = config('USE_L10N', default=False, cast=bool)
USE_TZ = config('USE_TZ', default=True, cast=bool)

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
SITE_URL = config('SITE_URL')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Instruct session-csrf to always produce tokens for anonymous users
ANON_ALWAYS = config('ANON_ALWAYS', default=True, cast=bool)

# Create account for new users.
BROWSERID_CREATE_USER = config('BROWSERID_CREATE_USER', default=True, cast=bool)
BROWSERID_VERIFY_CLASS = 'moderator.moderate.views.BrowserIDVerify'
BROWSERID_AUDIENCES = config('BROWSERID_AUDIENCES', cast=Csv())

# Path to redirect to on successful login.
LOGIN_REDIRECT_URL = config('LOGIN_REDIRECT_URL', default='/')
# Path to redirect to on unsuccessful login attempt.
LOGIN_REDIRECT_URL_FAILURE = config('LOGIN_REDIRECT_URL_FAILURE', default='/')
LOGOUT_REDIRECT_URL = config('LOGOUT_REDIRECT_URL', default='/')

# Mozillians API
MOZILLIANS_API_BASE = config('MOZILLIANS_API_BASE')
MOZILLIANS_API_KEY = config('MOZILLIANS_API_KEY', default='')
MOZILLIANS_API_APPNAME = config('MOZILLIANS_API_APPNAME', default='')

# Paginator items per page
ITEMS_PER_PAGE = config('ITEMS_PER_PAGE', default=10, cast=int)

# Sessions
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)

# Database
DATABASES = {
    'default': config('DATABASE_URL', cast=dj_database_url.parse)
}

# Enable debugging only if in dev env
if DEBUG:
    for backend in TEMPLATES:
        backend['OPTIONS']['debug'] = DEBUG
