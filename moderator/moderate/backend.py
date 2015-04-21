from django.conf import settings
from django.contrib.auth.models import User

from django_browserid.auth import BrowserIDBackend, default_username_algo

from moderator.moderate.mozillians import is_vouched, BadStatusCodeError


USERNAME_ALGO = getattr(settings, 'BROWSERID_USERNAME_ALGO',
                        default_username_algo)


class ModeratorBrowserIDBackend(BrowserIDBackend):

    def create_user(self, email):
        try:
            data = is_vouched(email)
        except BadStatusCodeError:
            data = None

        if data and data['is_vouched']:
            user = User.objects.create_user(username=USERNAME_ALGO(email),
                                            email=email)
            return user
