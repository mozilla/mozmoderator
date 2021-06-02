from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class ModeratorAuthBackend(OIDCAuthenticationBackend):
    """Override base authentication class."""

    def get_or_create_user(self, access_token, id_token, payload):
        """Get or create a new user only if they have one of the groups
        mentioned in the ALLOWED_LOGIN_GROUPS in the claims.
        """

        user_info = self.get_userinfo(access_token, id_token, payload)
        groups = user_info.get("https://sso.mozilla.com/claim/groups", [])

        # The user is not staff or NDA member. Return None
        if not any(x in groups for x in settings.ALLOWED_LOGIN_GROUPS):
            return None
        return super(ModeratorAuthBackend, self).get_or_create_user(
            access_token, id_token, payload
        )

    def update_user(self, user, claims):
        # Update user status (nda, staff based on assertions)
        profile = user.userprofile
        profile.avatar_url = claims.get("picture")
        profile.username = claims.get("nickname", "")
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.save()

        # Only staff members and members of the NDA group are allowed to login.
        # Because of this everyone will get the is_nda_member set to True.
        # If in the future more people are allowed to login this needs to be
        # available to only members of the ALLOWED_LOGIN_GROUPS
        profile.is_nda_member = True
        profile.save()
        return user
