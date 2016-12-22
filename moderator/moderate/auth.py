from django.conf import settings
from django.contrib.auth.models import User

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from moderator.moderate.mozillians import BadStatusCode, MozilliansClient, ResourceDoesNotExist


class ModeratorAuthBackend(OIDCAuthenticationBackend):
    """Override base authentication class."""

    def create_user(self, claims, **kwargs):
        """Create a new user only if there is a vouched mozillians.org account."""

        mozillians_client = MozilliansClient(settings.MOZILLIANS_API_URL,
                                             settings.MOZILLIANS_API_KEY)

        email = claims.get('email')
        try:
            mozillian_user = mozillians_client.lookup_user({'email': email})
        except (BadStatusCode, ResourceDoesNotExist):
            return None

        user_emails = []
        if mozillian_user['is_vouched']:
            for email_entry in mozillian_user['alternate_emails']:
                user_emails.append(email_entry['email'])
            user_emails.append(mozillian_user['email']['value'])
            users = User.objects.filter(email__in=user_emails)
            if users:
                return users[0]
            return super(ModeratorAuthBackend, self).create_user(claims, **kwargs)
        return None
