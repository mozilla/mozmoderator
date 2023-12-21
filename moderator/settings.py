# This is your project's main settings file that can be committed to your
# repo. If you need to override a setting locally, use local.py
import os

import dj_database_url
import pymysql
from decouple import Csv, config
from django_jinja.builtins import DEFAULT_EXTENSIONS

ROOT = os.path.dirname(os.path.dirname(__file__))
path = lambda *a: os.path.abspath(os.path.join(ROOT, *a))  # noqa
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
DEV = config("DEV", default=False, cast=bool)
SITE_URL = config("SITE_URL")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())


# Defines the views served for root URLs.
ROOT_URLCONF = "moderator.urls"

INSTALLED_APPS = [
    # Django apps
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "dal",
    "dal_select2",
    "django.contrib.admin",
    # Third party apps
    "axes",
    "mozilla_django_oidc",
    # Project specific apps
    "moderator.moderate",
]

if DEV:
    INSTALLED_APPS += ["django_extensions"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "axes.middleware.AxesMiddleware",
]

# List of finder classes that know how to find static files in
# various locations.
if not DEV:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "moderator.wsgi.application"

CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "NAME": "jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "match_extension": ".jinja",
            "newstyle_gettext": True,
            "context_processors": CONTEXT_PROCESSORS,
            "undefined": "jinja2.Undefined",
            "extensions": DEFAULT_EXTENSIONS,
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": CONTEXT_PROCESSORS},
    },
]


def COMPRESS_JINJA2_GET_ENVIRONMENT():
    from django.template import engines

    return engines["jinja2"].env


SITE_ID = 1

# Auth
# The first hasher in this list will be used for new passwords.
# Any other hasher in the list can be used for existing passwords.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "moderator.moderate.auth.ModeratorAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = path("media")
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = "/media/"
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = path("static")
STATIC_URL = "/static/"

# Internationalization
TIME_ZONE = config("TIME_ZONE", default="UTC")
USE_I18N = config("USE_I18N", default=False, cast=bool)
USE_L10N = config("USE_L10N", default=False, cast=bool)
USE_TZ = config("USE_TZ", default=True, cast=bool)

# Path to redirect to on successful login.
LOGIN_REDIRECT_URL = config("LOGIN_REDIRECT_URL", default="/")
# Path to redirect to on unsuccessful login attempt.
LOGIN_REDIRECT_URL_FAILURE = config("LOGIN_REDIRECT_URL_FAILURE", default="/")
LOGOUT_REDIRECT_URL = config("LOGOUT_REDIRECT_URL", default="/")

# Paginator items per page
ITEMS_PER_PAGE = config("ITEMS_PER_PAGE", default=10, cast=int)

# Sessions
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
SESSION_COOKIE_HTTPONLY = config("SESSION_COOKIE_HTTPONLY", default=True, cast=bool)
CSRF_USE_SESSIONS = True
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)

# Security Middleware
SECURE_CONTENT_TYPE_NOSNIFF = config(
    "SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool
)
SECURE_BROWSER_XSS_FILTER = config("SECURE_BROWSER_XSS_FILTER", default=True, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=15768000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True, cast=int
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Database
DATABASES = {"default": config("DATABASE_URL", cast=dj_database_url.parse)}
pymysql.install_as_MySQLdb()

# Enable debugging only if in dev env
if DEBUG:
    for backend in TEMPLATES:
        backend["OPTIONS"]["debug"] = DEBUG

# Sentry support
if SENTRY_DSN := config("SENTRY_DSN", None):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        sample_rate=config("SENTRY_SAMPLE_RATE", 1.0),
        traces_sample_rate=config("SENTRY_TRACES_SAMPLE_RATE", 0.01),
    )

# Django-CSP
CSP_DEFAULT_SRC = (
    "'self'",
    "https://*.mozilla.org",
    "https://*.mozilla.net",
    "https://mozillians.org",
)
CSP_IMG_SRC = (
    "'self'",
    "https://*.google-analytics.com",
    "https://*.gravatar.com",
    "https://*.wp.com",
    "https://cdn.mozillians.org",
)
CSP_SCRIPT_SRC = (
    "'self'",
    "https://*.google-analytics.com",
)


# Django OIDC
def _username_algo(email):
    import base64
    import hashlib

    try:
        from django.utils.encoding import smart_bytes
    except ImportError:
        from django.utils.encoding import smart_str as smart_bytes

    return base64.urlsafe_b64encode(hashlib.sha1(smart_bytes(email)).digest()).rstrip(
        b"="
    )


OIDC_OP_AUTHORIZATION_ENDPOINT = config("OIDC_OP_AUTHORIZATION_ENDPOINT", default="")
OIDC_OP_TOKEN_ENDPOINT = config("OIDC_OP_TOKEN_ENDPOINT", default="")
OIDC_OP_USER_ENDPOINT = config("OIDC_OP_USER_ENDPOINT", default="")
OIDC_RP_CLIENT_ID = config("OIDC_RP_CLIENT_ID", default="")
OIDC_RP_OIDC_RP_CLIENT_ID = config("OIDC_RP_CLIENT_ID", default="")
OIDC_RP_CLIENT_ID = config("OIDC_RP_CLIENT_ID", default="")
OIDC_RP_CLIENT_SECRET = config("OIDC_RP_CLIENT_SECRET", default="")
OIDC_RP_CLIENT_SECRET_ENCODED = config(
    "OIDC_RP_CLIENT_SECRET_ENCODED", default=True, cast=bool
)
OIDC_CALLBACK_CLASS = "moderator.moderate.views.OIDCCallbackView"
OIDC_USERNAME_ALGO = _username_algo
OIDC_STORE_ACCESS_TOKEN = config("OIDC_STORE_ACCESS_TOKEN", default=True, cast=bool)
OIDC_RP_SIGN_ALGO = config("OIDC_RP_SIGN_ALGO", default="RS256")
OIDC_OP_JWKS_ENDPOINT = config("OIDC_OP_JWKS_ENDPOINT", default="")
OIDC_RP_SCOPES = "openid email profile"

# Allowed groups a user must have to login
ALLOWED_LOGIN_GROUPS = [
    "team_moco",
    "team_mofo",
    "team_mozillaonline",
    "hris_is_staff",
    "mozilliansorg_nda",
    "mozilliansorg_contingentworkernda",
]

# Django 3.2 Autofield
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Enable dev login
ENABLE_DEV_LOGIN = config("ENABLE_DEV_LOGIN", default=False, cast=bool)

# Enable debug toolbar
ENABLE_DEBUG_TOOLBAR = config("ENABLE_DEBUG_TOOLBAR", default=False, cast=bool)


def show_toolbar_callback(*args):
    return DEBUG and ENABLE_DEBUG_TOOLBAR


SHOW_DEBUG_TOOLBAR = show_toolbar_callback()

if SHOW_DEBUG_TOOLBAR:
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": "moderator.settings.show_toolbar_callback"
    }

    INSTALLED_APPS = INSTALLED_APPS + ["debug_toolbar"]

    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

# Email setup
FROM_NOREPLY = config(
    "FROM_NOREPLY",
    default="Mozilla Moderator <no-reply@moderator.mozilla.org>",
)

# Django Axes
AXES_ENABLED = config("AXES_ENABLED", default=True, cast=bool)
AXES_IPWARE_PROXY_COUNT = config("AXES_IPWARE_PROXY_COUNT", default=1, cast=int)
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
]

if DEV and DEBUG:
    EMAIL_LOGGING_REAL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "mailcatcher"
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
else:
    # AWS SES configuration
    EMAIL_BACKEND = "django_ses.SESBackend"
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_SES_REGION_NAME = config("AWS_DEFAULT_REGION", default="us-west-2")
    AWS_SES_REGION_ENDPOINT = config(
        "AWS_REGION_ENDPOINT", default="email.us-west-2.amazonaws.com"
    )
