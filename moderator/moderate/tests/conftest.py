import pytest


def pytest_configure(config):
    from django.conf import settings

    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_SECURE = False
    settings.SECURE_HSTS_SECONDS = 0


@pytest.fixture
def make_user(db):
    """Build a user whose profile is flagged as staff or NDA community."""

    def _make_user(username, is_employee=False, superuser=False):
        from django.contrib.auth.models import User

        create = (
            User.objects.create_superuser if superuser else User.objects.create_user
        )
        user = create(username=username, email=f"{username}@example.com", password="x")
        profile = user.userprofile
        profile.is_employee = is_employee
        profile.save()
        return user

    return _make_user
