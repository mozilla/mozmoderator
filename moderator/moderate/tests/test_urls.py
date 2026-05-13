from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils.timezone import now as django_now

from moderator.moderate.models import Event


@pytest.mark.django_db
def test_main_page_anonymous_renders():
    """Anonymous GET / should render (no 5xx)."""
    client = Client()
    resp = client.get("/")
    assert resp.status_code in (200, 302)


@pytest.mark.django_db
def test_admin_login_renders():
    client = Client()
    resp = client.get("/admin/login/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_create_event_requires_login():
    client = Client()
    resp = client.get("/event/new")
    assert resp.status_code in (302, 403)


@pytest.mark.django_db
def test_authenticated_user_can_create_event():
    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="pw"
    )
    client = Client()
    client.force_login(user)
    resp = client.get("/event/new")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_user_autocomplete_returns_matches():
    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="x"
    )
    User.objects.create_user(
        username="bob", email="bob@example.com", password="x"
    )
    client = Client()
    client.force_login(user)
    resp = client.get("/u/user-autocomplete/?q=alic")
    assert resp.status_code == 200
    data = resp.json()
    usernames = [r["text"] for r in data["results"]]
    assert any("alice" in name for name in usernames)
    assert not any("bob" in name for name in usernames)


@pytest.mark.django_db
def test_user_autocomplete_anonymous_redirects():
    client = Client()
    resp = client.get("/u/user-autocomplete/")
    assert resp.status_code in (302, 403)


def _make_past_event(creator):
    event = Event.objects.create(
        name="Past Event",
        event_date=django_now().date() - timedelta(days=1),
        created_by=creator,
    )
    event.moderators.set([creator])
    return event


@pytest.mark.django_db
def test_archive_event_moderator_can_archive_past_event():
    creator = User.objects.create_user(
        username="creator", email="creator@example.com", password="x"
    )
    event = _make_past_event(creator)
    client = Client()
    client.force_login(creator)
    resp = client.post(f"/e/{event.slug}/archive")
    assert resp.status_code == 302
    event.refresh_from_db()
    assert event.archived is True


@pytest.mark.django_db
def test_archive_event_non_moderator_cannot_archive():
    creator = User.objects.create_user(
        username="creator", email="creator@example.com", password="x"
    )
    intruder = User.objects.create_user(
        username="intruder", email="intruder@example.com", password="x"
    )
    event = _make_past_event(creator)
    client = Client()
    client.force_login(intruder)
    resp = client.post(f"/e/{event.slug}/archive")
    assert resp.status_code == 404
    event.refresh_from_db()
    assert event.archived is False


@pytest.mark.django_db
def test_archive_event_anonymous_redirects():
    creator = User.objects.create_user(
        username="creator", email="creator@example.com", password="x"
    )
    event = _make_past_event(creator)
    client = Client()
    resp = client.post(f"/e/{event.slug}/archive")
    assert resp.status_code in (302, 403)
    event.refresh_from_db()
    assert event.archived is False


@pytest.mark.django_db
def test_archive_event_rejects_future_event():
    creator = User.objects.create_user(
        username="creator", email="creator@example.com", password="x"
    )
    event = Event.objects.create(
        name="Future Event",
        event_date=django_now().date() + timedelta(days=7),
        created_by=creator,
    )
    event.moderators.set([creator])
    client = Client()
    client.force_login(creator)
    resp = client.post(f"/e/{event.slug}/archive")
    assert resp.status_code == 302
    event.refresh_from_db()
    assert event.archived is False


@pytest.mark.django_db
def test_archive_event_get_not_allowed():
    """The endpoint accepts POST only (state-changing action)."""
    creator = User.objects.create_user(
        username="creator", email="creator@example.com", password="x"
    )
    event = _make_past_event(creator)
    client = Client()
    client.force_login(creator)
    resp = client.get(f"/e/{event.slug}/archive")
    assert resp.status_code == 405
    event.refresh_from_db()
    assert event.archived is False
