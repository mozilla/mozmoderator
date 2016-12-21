from django.conf import settings

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from moderator.moderate.mozillians import BadStatusCode, MozilliansClient, ResourceDoesNotExist


class ModeratorAuthBackend(OIDCAuthenticationBackend):
    """Override base authentication class."""

    def create_user(self, claims, **kwargs):
        """Create a new user only if there is a vouched mozillians.org account."""

        mozillians_client = MozilliansClient(settings.MOZILLIANS_API_URL,
                                             settings.MOZILLIANS_API_KEY)

        is_vouched = False
        email = claims.get('email')
        try:
            _, is_vouched = mozillians_client.is_vouched(email)
        except (BadStatusCode, ResourceDoesNotExist):
            return None

        if is_vouched:
            return super(ModeratorAuthBackend, self).create_user(claims, **kwargs)
        return None
