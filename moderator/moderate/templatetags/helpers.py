import json

from base64 import b64encode

from django.conf import settings
from django.core.urlresolvers import reverse
from django_jinja import library

from mozilla_django_oidc.utils import absolutify


@library.global_function
def user_voted(question, user):
    """Check if a user has already voted."""
    return question.votes.filter(user=user).exists()


@library.global_function
def auth0_js_settings():
    """Client side configuration as base64 encoded JSON string"""

    obj = {
        'AUTH0_CALLBACK_URL': absolutify(reverse('oidc_authentication_callback')),
        'AUTH0_DOMAIN': settings.AUTH0_DOMAIN,
        'AUTH0_CLIENT_ID': settings.OIDC_RP_CLIENT_ID
    }

    json_str = json.dumps(obj)

    return b64encode(json_str)
