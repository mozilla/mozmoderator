import bisect
from re import compile, escape

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

_USERNAME_CHAR_RE = compile(UnicodeUsernameValidator.regex)


def normalize_username(username):
    """Remove any characters not accepted by Django's UnicodeUsernameValidator."""
    normalized = ""
    for char in username:
        if not _USERNAME_CHAR_RE.match(char):
            continue
        normalized += char
    return normalized


def suggest_username(email):
    """Derive a unique username from an email address.

    Mirrors kitsune.users.utils.suggest_username: take the email local-part,
    drop characters Django rejects, then if the base collides with an
    existing User, append the smallest available integer suffix (gap-filling).
    """
    username = normalize_username(email.split("@", 1)[0])

    username_regex = r"^{}[0-9]*$".format(escape(username))
    existing_usernames = list(
        User.objects.filter(username__iregex=username_regex).values_list(
            "username", flat=True
        )
    )

    if existing_usernames:
        ids = []
        for existing in existing_usernames:
            i = existing[len(username) :]
            if i:
                i = int(i)
                bisect.insort(ids, i)
            else:
                ids.insert(0, 0)

        for index, i in enumerate(ids):
            if index + 1 < len(ids):
                suggested_number = i + 1
                if suggested_number != ids[index + 1] and suggested_number not in ids:
                    break

        username = "{}{}".format(username, i + 1)

    return username


def is_employee_groups(groups):
    """True if `groups` contains one of the staff groups.

    Employees reach the site through their LDAP derived groups, while NDA
    community members only ever carry a group from NDA_LOGIN_GROUPS.
    """
    return not set(groups).isdisjoint(settings.EMPLOYEE_LOGIN_GROUPS)


def is_legacy_username(username):
    """True if `username` contains characters Django's UnicodeUsernameValidator rejects.

    Used to detect users whose User.username is still the opaque OIDC `uid`
    (e.g. `ad|Mozilla-LDAP|jsmith`) so it can be backfilled with a derived
    value on next login.
    """
    validator = UnicodeUsernameValidator()
    try:
        validator(username)
    except ValidationError:
        return True
    return False
