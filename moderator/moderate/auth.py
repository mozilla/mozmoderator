from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from moderator.moderate.mozillians import is_vouched, BadStatusCodeError


class ModeratorAuthBackend(OIDCAuthenticationBackend):
    def create_user(self, email, **kwargs):
        try:
            data = is_vouched(email)
        except BadStatusCodeError:
            data = None

        if data and data['is_vouched']:
            return super(ModeratorAuthBackend, self).create_user(email, **kwargs)
        return None
