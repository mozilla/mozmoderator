import pytest
from django.contrib.auth.models import User
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from moderator.moderate.auth import GROUPS_CLAIM, ModeratorAuthBackend


def test_get_userinfo_asks_the_provider_once_per_access_token(monkeypatch):
    """get_or_create_user and the base implementation share one lookup."""
    calls = []

    def fake_get_userinfo(self, access_token, id_token, payload):
        calls.append(access_token)
        return {"email": "jane@mozilla.com", GROUPS_CLAIM: ["team_moco"]}

    monkeypatch.setattr(OIDCAuthenticationBackend, "get_userinfo", fake_get_userinfo)
    backend = ModeratorAuthBackend()

    assert backend.get_userinfo("token", None, {}) == backend.get_userinfo(
        "token", None, {}
    )
    assert calls == ["token"]

    backend.get_userinfo("other-token", None, {})
    assert calls == ["token", "other-token"]


@pytest.mark.django_db
def test_create_user_uses_email_derived_username():
    backend = ModeratorAuthBackend()
    user = backend.create_user({"email": "newperson@mozilla.com"})
    assert user.username == "newperson"
    assert user.email == "newperson@mozilla.com"


@pytest.mark.django_db
def test_update_user_backfills_legacy_username():
    user = User.objects.create_user(
        username="ad|Mozilla-LDAP|jane", email="jane@mozilla.com"
    )
    backend = ModeratorAuthBackend()
    backend.update_user(user, {"email": "jane@mozilla.com"})
    user.refresh_from_db()
    assert user.username == "jane"


@pytest.mark.django_db
def test_update_user_leaves_clean_username_alone():
    user = User.objects.create_user(username="jane", email="jane@mozilla.com")
    backend = ModeratorAuthBackend()
    backend.update_user(user, {"email": "jane@mozilla.com"})
    user.refresh_from_db()
    assert user.username == "jane"


@pytest.mark.django_db
def test_update_user_backfill_resolves_collision():
    # Another user already owns the obvious derivation.
    User.objects.create_user(username="jane", email="other@mozilla.com")
    user = User.objects.create_user(
        username="ad|Mozilla-LDAP|jane2", email="jane@mozilla.com"
    )
    backend = ModeratorAuthBackend()
    backend.update_user(user, {"email": "jane@mozilla.com"})
    user.refresh_from_db()
    assert user.username == "jane1"


@pytest.mark.django_db
def test_create_user_flags_employee_on_first_login():
    """First login goes through create_user, not update_user."""
    backend = ModeratorAuthBackend()
    user = backend.create_user(
        {"email": "newperson@mozilla.com", GROUPS_CLAIM: ["team_moco"]}
    )
    assert user.userprofile.is_employee is True


@pytest.mark.django_db
def test_create_user_does_not_flag_community_member():
    backend = ModeratorAuthBackend()
    user = backend.create_user(
        {"email": "contributor@example.com", GROUPS_CLAIM: ["mozilliansorg_nda"]}
    )
    assert user.userprofile.is_employee is False


@pytest.mark.django_db
def test_update_user_flags_employee():
    user = User.objects.create_user(username="jane", email="jane@mozilla.com")
    backend = ModeratorAuthBackend()
    backend.update_user(
        user, {"email": "jane@mozilla.com", GROUPS_CLAIM: ["team_mzla"]}
    )
    user.userprofile.refresh_from_db()
    assert user.userprofile.is_employee is True


@pytest.mark.django_db
def test_update_user_clears_employee_flag_when_claim_drops_staff_group():
    """A contributor who left staff must lose access to employee only events."""
    user = User.objects.create_user(username="jane", email="jane@mozilla.com")
    profile = user.userprofile
    profile.is_employee = True
    profile.save()

    backend = ModeratorAuthBackend()
    backend.update_user(
        user, {"email": "jane@example.com", GROUPS_CLAIM: ["mozilliansorg_nda"]}
    )
    profile.refresh_from_db()
    assert profile.is_employee is False


@pytest.mark.django_db
def test_update_user_updates_email_before_deriving_username():
    # User's email in claims differs from stored email; the derivation
    # should use the new email, not the stale one.
    user = User.objects.create_user(
        username="ad|Mozilla-LDAP|x", email="old@mozilla.com"
    )
    backend = ModeratorAuthBackend()
    backend.update_user(user, {"email": "newname@mozilla.com"})
    user.refresh_from_db()
    assert user.email == "newname@mozilla.com"
    assert user.username == "newname"
