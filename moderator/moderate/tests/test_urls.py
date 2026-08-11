from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.utils.timezone import now as django_now

from moderator.moderate.models import Event, Question


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
def test_create_event_page_explains_locked_nda_choice(make_user):
    """A community member sees the option, disabled, rather than nothing."""
    client = Client()
    client.force_login(make_user("contributor"))
    resp = client.get("/event/new")
    assert b"NDA Community members" in resp.content
    assert b"Only staff can change who an event is open to." in resp.content


@pytest.mark.django_db
def test_create_event_page_leaves_nda_choice_open_to_employee(make_user):
    client = Client()
    client.force_login(make_user("staff", is_employee=True))
    resp = client.get("/event/new")
    assert b"NDA Community members" in resp.content
    assert b"Only staff can change who an event is open to." not in resp.content


@pytest.mark.django_db
def test_user_autocomplete_returns_matches():
    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="x"
    )
    User.objects.create_user(username="bob", email="bob@example.com", password="x")
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


def _make_events(archived=False):
    staff_only = Event.objects.create(
        name="Staff Only Event", allow_nda_community=False, archived=archived
    )
    community = Event.objects.create(
        name="Community Welcome Event", allow_nda_community=True, archived=archived
    )
    return staff_only, community


@pytest.mark.django_db
def test_index_hides_staff_only_events_from_community_member(make_user):
    _make_events()
    client = Client()
    client.force_login(make_user("contributor"))
    resp = client.get("/")
    assert b"Community Welcome Event" in resp.content
    assert b"Staff Only Event" not in resp.content


@pytest.mark.django_db
def test_index_shows_every_event_to_employee(make_user):
    _make_events()
    client = Client()
    client.force_login(make_user("staff", is_employee=True))
    resp = client.get("/")
    assert b"Community Welcome Event" in resp.content
    assert b"Staff Only Event" in resp.content


@pytest.mark.django_db
def test_archive_hides_staff_only_events_from_community_member(make_user):
    _make_events(archived=True)
    client = Client()
    client.force_login(make_user("contributor"))
    resp = client.get("/archives")
    assert b"Community Welcome Event" in resp.content
    assert b"Staff Only Event" not in resp.content


@pytest.mark.django_db
def test_archive_shows_every_event_to_employee(make_user):
    _make_events(archived=True)
    client = Client()
    client.force_login(make_user("staff", is_employee=True))
    resp = client.get("/archives")
    assert b"Community Welcome Event" in resp.content
    assert b"Staff Only Event" in resp.content


@pytest.mark.django_db
def test_event_page_404s_for_community_member_on_staff_only_event(make_user):
    staff_only, _ = _make_events()
    client = Client()
    client.force_login(make_user("contributor"))
    assert client.get(f"/e/{staff_only.slug}/").status_code == 404


@pytest.mark.django_db
def test_event_page_open_to_community_member_when_opted_in(make_user):
    _, community = _make_events()
    client = Client()
    client.force_login(make_user("contributor"))
    assert client.get(f"/e/{community.slug}/").status_code == 200


@pytest.mark.django_db
def test_event_page_open_to_employee_either_way(make_user):
    staff_only, community = _make_events()
    client = Client()
    client.force_login(make_user("staff", is_employee=True))
    assert client.get(f"/e/{staff_only.slug}/").status_code == 200
    assert client.get(f"/e/{community.slug}/").status_code == 200


@pytest.mark.django_db
def test_event_page_open_to_community_moderator_of_staff_only_event(make_user):
    """Moderators keep access so the moderation queue stays reachable."""
    staff_only, _ = _make_events()
    contributor = make_user("contributor")
    staff_only.moderators.set([contributor])
    client = Client()
    client.force_login(contributor)
    assert client.get(f"/e/{staff_only.slug}/").status_code == 200


@pytest.mark.django_db
def test_index_lists_staff_only_event_a_community_member_moderates(make_user):
    """An event the user can open has to be reachable from the listing too."""
    staff_only, _ = _make_events()
    contributor = make_user("contributor")
    staff_only.moderators.set([contributor])
    client = Client()
    client.force_login(contributor)
    assert b"Staff Only Event" in client.get("/").content


@pytest.mark.django_db
def test_archive_lists_staff_only_event_a_community_member_moderates(make_user):
    staff_only, _ = _make_events(archived=True)
    contributor = make_user("contributor")
    staff_only.moderators.set([contributor])
    client = Client()
    client.force_login(contributor)
    assert b"Staff Only Event" in client.get("/archives").content


@pytest.mark.django_db
def test_index_shows_every_event_to_superuser_without_employee_flag(make_user):
    """The email based backfill can leave an admin account unflagged."""
    _make_events()
    client = Client()
    client.force_login(make_user("root", superuser=True))
    resp = client.get("/")
    assert b"Community Welcome Event" in resp.content
    assert b"Staff Only Event" in resp.content


@pytest.mark.django_db
def test_reply_url_404s_for_question_from_another_event(make_user):
    """The question has to belong to the event in the URL."""
    staff_only, community = _make_events()
    secret = Question.objects.create(
        event=staff_only, question="Secret staff only question.", is_accepted=True
    )
    client = Client()
    client.force_login(make_user("contributor"))
    resp = client.get(f"/e/{community.slug}/q/{secret.id}/reply")
    assert resp.status_code == 404
    assert b"Secret staff only question." not in resp.content


@pytest.mark.django_db
def test_moderate_url_404s_for_question_from_another_event(make_user):
    """A moderator of one event must not moderate another event's questions."""
    staff_only, community = _make_events()
    contributor = make_user("contributor")
    community.moderators.set([contributor])
    other = Question.objects.create(
        event=staff_only, question="A question with enough text.", is_accepted=None
    )
    client = Client()
    client.force_login(contributor)
    resp = client.get(f"/e/{community.slug}/moderate/{other.id}/accepted")
    assert resp.status_code == 404
    other.refresh_from_db()
    assert other.is_accepted is None


@pytest.mark.django_db
def test_upvote_404s_for_community_member_on_staff_only_event(make_user):
    staff_only, _ = _make_events()
    question = Question.objects.create(
        event=staff_only, question="A question with enough text.", is_accepted=True
    )
    client = Client()
    client.force_login(make_user("contributor"))
    resp = client.post(
        f"/q/{question.id}/upvote", headers={"x-requested-with": "XMLHttpRequest"}
    )
    assert resp.status_code == 404
    assert question.votes.count() == 0


@pytest.mark.django_db
def test_upvote_404s_for_unknown_question(make_user):
    client = Client()
    client.force_login(make_user("staff", is_employee=True))
    resp = client.post("/q/4711/upvote", headers={"x-requested-with": "XMLHttpRequest"})
    assert resp.status_code == 404


@pytest.mark.django_db
def test_upvote_404s_for_non_numeric_question_id(make_user):
    client = Client()
    client.force_login(make_user("staff", is_employee=True))
    resp = client.post(
        "/q/not-a-number/upvote", headers={"x-requested-with": "XMLHttpRequest"}
    )
    assert resp.status_code == 404


@pytest.mark.django_db
def test_upvote_respects_voting_switch_on_nda_event(make_user):
    """Opting an event in to the NDA community must not re-enable voting."""
    event = Event.objects.create(
        name="No Voting", allow_nda_community=True, users_can_vote=False
    )
    question = Question.objects.create(
        event=event, question="A question with enough text.", is_accepted=True
    )
    client = Client()
    client.force_login(make_user("staff", is_employee=True))
    resp = client.post(
        f"/q/{question.id}/upvote", headers={"x-requested-with": "XMLHttpRequest"}
    )
    assert resp.status_code == 302
    assert question.votes.count() == 0


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
