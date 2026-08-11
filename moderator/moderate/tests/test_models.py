import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count, Q

from moderator.moderate.models import Event, MozillianProfile, Question, Vote


@pytest.mark.django_db
def test_user_post_save_creates_mozillian_profile():
    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="x"
    )
    assert MozillianProfile.objects.filter(user=user).exists()
    assert user.userprofile.username == "alice"


@pytest.mark.django_db
def test_event_save_generates_slug():
    user = User.objects.create_user(username="bob", email="bob@example.com")
    event = Event.objects.create(name="My Test Event", created_by=user)
    assert event.slug
    assert event.slug.startswith("my-test-event")


@pytest.mark.django_db
def test_event_str_returns_name():
    user = User.objects.create_user(username="bob", email="bob@example.com")
    event = Event.objects.create(name="Hello", created_by=user)
    assert str(event) == "Hello"


@pytest.mark.django_db
def test_question_full_clean_rejects_short_question():
    user = User.objects.create_user(username="c", email="c@example.com")
    event = Event.objects.create(name="E", created_by=user)
    q = Question(asked_by=user, event=event, question="short")
    with pytest.raises(ValidationError):
        q.full_clean()


@pytest.mark.django_db
def test_question_full_clean_accepts_valid_length():
    user = User.objects.create_user(username="d", email="d@example.com")
    event = Event.objects.create(name="E", created_by=user)
    q = Question(asked_by=user, event=event, question="This is a valid question.")
    q.full_clean()


@pytest.mark.django_db
def test_vote_unique_together():
    user = User.objects.create_user(username="e", email="e@example.com")
    event = Event.objects.create(name="E", created_by=user)
    q = Question.objects.create(
        asked_by=user, event=event, question="A long enough question body."
    )
    Vote.objects.create(user=user, question=q)
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        Vote.objects.create(user=user, question=q)


@pytest.mark.django_db
def test_event_questions_count_property():
    user = User.objects.create_user(username="f", email="f@example.com")
    event = Event.objects.create(name="E", created_by=user)
    Question.objects.create(
        asked_by=user, event=event, question="First valid question body."
    )
    Question.objects.create(
        asked_by=user, event=event, question="Second valid question body."
    )
    assert event.questions_count == 2


@pytest.mark.django_db
def test_visible_to_returns_opted_in_and_moderated_events(make_user):
    contributor = make_user("contributor")
    community = Event.objects.create(name="Community", allow_nda_community=True)
    moderated = Event.objects.create(name="Moderated", allow_nda_community=False)
    moderated.moderators.set([contributor])
    Event.objects.create(name="Staff Only", allow_nda_community=False)

    visible = Event.objects.visible_to(contributor)
    assert set(visible.values_list("name", flat=True)) == {"Community", "Moderated"}
    assert community in visible


@pytest.mark.django_db
def test_visible_to_returns_everything_for_employees_and_superusers(make_user):
    Event.objects.create(name="Staff Only", allow_nda_community=False)
    Event.objects.create(name="Community", allow_nda_community=True)

    for user in [
        make_user("staff", is_employee=True),
        make_user("root", superuser=True),
    ]:
        assert Event.objects.visible_to(user).count() == 2


@pytest.mark.django_db
def test_visible_to_does_not_inflate_annotations(make_user):
    """The moderator clause must not join and double the Count() annotations."""
    contributor = make_user("contributor")
    event = Event.objects.create(name="Staff Only", allow_nda_community=False)
    event.moderators.set([contributor, make_user("staff", is_employee=True)])
    for i in range(3):
        Question.objects.create(
            event=event, question=f"Question number {i} body text.", is_accepted=True
        )

    annotated = (
        Event.objects.visible_to(contributor)
        .annotate(
            approved_count=Count("questions", filter=Q(questions__is_accepted=True))
        )
        .get()
    )
    assert annotated.approved_count == 3
