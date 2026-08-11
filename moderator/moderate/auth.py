from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from moderator.moderate.utils import (
    is_employee_groups,
    is_legacy_username,
    suggest_username,
)

GROUPS_CLAIM = "https://sso.mozilla.com/claim/groups"


class ModeratorAuthBackend(OIDCAuthenticationBackend):
    """Override base authentication class."""

    _userinfo = None
    _userinfo_access_token = None

    def get_userinfo(self, access_token, id_token, payload):
        """Fetch the claims once per login.

        `get_or_create_user` needs them to gate the login and the base
        implementation asks the provider for them again right afterwards.
        """
        if self._userinfo is None or access_token != self._userinfo_access_token:
            self._userinfo = super(ModeratorAuthBackend, self).get_userinfo(
                access_token, id_token, payload
            )
            self._userinfo_access_token = access_token
        return self._userinfo

    def get_or_create_user(self, access_token, id_token, payload):
        """Get or create a new user only if they have one of the groups
        mentioned in the ALLOWED_LOGIN_GROUPS in the claims.
        """
        user_info = self.get_userinfo(access_token, id_token, payload)
        groups = user_info.get(GROUPS_CLAIM, [])

        # The user is not staff or NDA member. Return None
        if not any(x in groups for x in settings.ALLOWED_LOGIN_GROUPS):
            return None
        return super(ModeratorAuthBackend, self).get_or_create_user(
            access_token, id_token, payload
        )

    def create_user(self, claims):
        user = super(ModeratorAuthBackend, self).create_user(claims)
        self.update_profile(user, claims)
        return user

    def update_user(self, user, claims):
        email = claims.get("email")
        if email and user.email != email:
            user.email = email
        if is_legacy_username(user.username):
            user.username = suggest_username(user.email)
        user.save()
        self.update_profile(user, claims)
        return user

    def update_profile(self, user, claims):
        """Refresh the profile fields derived from the OIDC claims."""
        profile = user.userprofile
        profile.avatar_url = claims.get("avatar", "")
        profile.is_employee = is_employee_groups(claims.get(GROUPS_CLAIM, []))
        profile.save()
