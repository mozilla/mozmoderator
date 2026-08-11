import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings

from moderator.moderate.utils import (
    is_employee_groups,
    is_legacy_username,
    normalize_username,
    suggest_username,
)


def test_normalize_username_strips_space():
    assert normalize_username("foo bar") == "foobar"


def test_normalize_username_strips_pipe():
    assert normalize_username("ad|Mozilla-LDAP|jsmith") == "adMozilla-LDAPjsmith"


def test_normalize_username_keeps_allowed_chars():
    # UnicodeUsernameValidator allows letters, digits, _, ., @, +, -
    assert normalize_username("user.name+tag-1_2@x") == "user.name+tag-1_2@x"


def test_normalize_username_strips_slash():
    assert normalize_username("foobar /1") == "foobar1"


def test_normalize_username_empty_input_returns_empty():
    assert normalize_username("") == ""


@pytest.mark.django_db
def test_suggest_username_no_collision():
    assert suggest_username("someuser@test.com") == "someuser"


@pytest.mark.django_db
def test_suggest_username_first_collision():
    User.objects.create_user(username="someuser", email="x@y.com")
    assert suggest_username("someuser@test.com") == "someuser1"


@pytest.mark.django_db
def test_suggest_username_gap_fills():
    User.objects.create_user(username="someuser", email="a@b.com")
    User.objects.create_user(username="someuser4", email="c@d.com")
    assert suggest_username("someuser@test.com") == "someuser1"


@pytest.mark.django_db
def test_suggest_username_case_insensitive_collision():
    User.objects.create_user(username="ricky", email="r1@x.com")
    User.objects.create_user(username="Ricky1", email="r2@x.com")
    User.objects.create_user(username="ricky33", email="r3@x.com")
    assert suggest_username("rIcky@test.com") == "rIcky2"


@pytest.mark.django_db
def test_suggest_username_leading_zero_suffix():
    User.objects.create_user(username="user", email="u0@x.com")
    User.objects.create_user(username="user01", email="u01@x.com")
    User.objects.create_user(username="user1", email="u1@x.com")
    User.objects.create_user(username="user2", email="u2@x.com")
    assert suggest_username("user@test.com") == "user3"


@pytest.mark.django_db
def test_suggest_username_strips_invalid_chars_from_local_part():
    # The space in "foo bar" is invalid; normalization drops it before
    # collision lookup.
    assert suggest_username("foo bar@x.com") == "foobar"


def test_is_legacy_username_rejects_pipe():
    assert is_legacy_username("ad|Mozilla-LDAP|jsmith") is True


def test_is_legacy_username_rejects_space():
    assert is_legacy_username("foo bar") is True


def test_is_legacy_username_rejects_empty():
    assert is_legacy_username("") is True


def test_is_legacy_username_accepts_plain():
    assert is_legacy_username("jsmith") is False


def test_is_legacy_username_accepts_with_suffix():
    assert is_legacy_username("jsmith42") is False


def test_is_legacy_username_accepts_with_special_chars():
    # ., @, +, -, _ are all allowed by UnicodeUsernameValidator.
    assert is_legacy_username("user.name+tag-1_2") is False


def test_is_employee_groups_accepts_staff_group():
    assert is_employee_groups(["team_moco"]) is True


def test_is_employee_groups_rejects_nda_only():
    assert is_employee_groups(["mozilliansorg_nda"]) is False


def test_is_employee_groups_rejects_contingent_worker_nda():
    assert is_employee_groups(["mozilliansorg_contingentworkernda"]) is False


def test_is_employee_groups_accepts_staff_who_is_also_nda():
    assert is_employee_groups(["mozilliansorg_nda", "team_mzla"]) is True


def test_is_employee_groups_ignores_unknown_groups():
    """A group outside the configured groups must not confer staff status."""
    assert is_employee_groups(["mozilliansorg_random_community_group"]) is False


def test_is_employee_groups_rejects_empty():
    assert is_employee_groups([]) is False


@override_settings(EMPLOYEE_LOGIN_GROUPS=["team_standards"])
def test_is_employee_groups_matches_names_exactly():
    """A staff group whose name happens to contain "nda" is still staff."""
    assert is_employee_groups(["team_standards"]) is True


def test_employee_and_nda_groups_are_disjoint():
    assert set(settings.EMPLOYEE_LOGIN_GROUPS).isdisjoint(settings.NDA_LOGIN_GROUPS)
    assert set(settings.ALLOWED_LOGIN_GROUPS) == set(
        settings.EMPLOYEE_LOGIN_GROUPS
    ) | set(settings.NDA_LOGIN_GROUPS)
