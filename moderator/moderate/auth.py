from django.conf import settings
from django.contrib.auth.models import User

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from moderator.moderate.mozillians import BadStatusCode, MozilliansClient, ResourceDoesNotExist


class ModeratorAuthBackend(OIDCAuthenticationBackend):
    """Override base authentication class."""

    def __init__(self, *args, **kwargs):
        """Add the mozillian user in the init method."""
        self.mozillian_user = None
        self.mozillians_client = MozilliansClient(settings.MOZILLIANS_API_URL,
                                                  settings.MOZILLIANS_API_KEY)

        super(ModeratorAuthBackend, self).__init__(*args, **kwargs)

    def create_user(self, claims, **kwargs):
        """Create a new user only if there is a vouched mozillians.org account."""

        email = claims.get('email')
        try:
            self.mozillian_user = self.mozillians_client.lookup_user({'email': email})
        except (BadStatusCode, ResourceDoesNotExist):
            return None

        user_emails = []
        if self.mozillian_user['is_vouched']:
            for email_entry in self.mozillian_user['alternate_emails']:
                user_emails.append(email_entry['email'])
            user_emails.append(self.mozillian_user['email']['value'])
            users = User.objects.filter(email__in=user_emails)
            if users:
                return users[0]
            return super(ModeratorAuthBackend, self).create_user(claims, **kwargs)
        return None

    def authenticate(self, **kwargs):
        """Override authenticate method of the OIDC lib."""
        user = super(ModeratorAuthBackend, self).authenticate(**kwargs)
        if not user:
            return None
        profile = user.userprofile
        profile.is_nda_member = False

        try:
            self.mozillian_user = self.mozillians_client.lookup_user({'email': user.email})
        except (BadStatusCode, ResourceDoesNotExist):
            return None

        # Get alternate emails
        user_email_domains = [user.email.split('@')[1]]
        for email_resource in self.mozillian_user['alternate_emails']:
            user_email_domains.append(email_resource['email'].split('@')[1])

        user_groups = [group['name'] for group in self.mozillian_user['groups']['value']]

        # Check if the user is member of the NDA group on each login.
        # Automatically add users with @mozilla* email in the nda group.
        if ([email_domain for email_domain in user_email_domains
             if email_domain in settings.TRUSTED_MOZILLA_DOMAINS] or
                settings.NDA_GROUP in user_groups):
            # Find an exact match for the username, eg foo != foo1
            profile.is_nda_member = True

        if profile.username != self.mozillian_user['username']:
            profile.username = self.mozillian_user['username']
            if self.mozillian_user['photo']['privacy'] == 'Public':
                profile.avatar_url = self.mozillian_user['photo']['value']
        profile.save()
        return user
