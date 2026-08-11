import pytest

from moderator.moderate.forms import EventForm, QuestionForm
from moderator.moderate.models import Event


def _event_data(user, **overrides):
    data = {"name": "Test event", "body": "", "moderators": [user.pk]}
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_question_form_rejects_too_short_text():
    form = QuestionForm(data={"question": "tiny"})
    assert not form.is_valid()
    assert "question" in form.errors


@pytest.mark.django_db
def test_question_form_rejects_too_long_text():
    form = QuestionForm(data={"question": "x" * 501})
    assert not form.is_valid()
    assert "question" in form.errors


@pytest.mark.django_db
def test_question_form_accepts_valid_text():
    form = QuestionForm(data={"question": "This is a perfectly valid question."})
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_event_form_forces_nda_for_community_member(make_user):
    """A community member would lose sight of an event that is not opted in."""
    user = make_user("contributor")
    form = EventForm(_event_data(user, is_nda=False), user=user)
    assert form.is_valid(), form.errors
    assert form.save().is_nda is True


@pytest.mark.django_db
def test_event_form_forces_nda_when_community_member_omits_the_field(make_user):
    user = make_user("contributor")
    form = EventForm(_event_data(user), user=user)
    assert form.is_valid(), form.errors
    assert form.save().is_nda is True


@pytest.mark.django_db
def test_event_form_lets_employee_opt_out(make_user):
    user = make_user("staff", is_employee=True)
    form = EventForm(_event_data(user, is_nda=False), user=user)
    assert form.is_valid(), form.errors
    assert form.save().is_nda is False


@pytest.mark.django_db
def test_event_form_lets_employee_opt_in(make_user):
    user = make_user("staff", is_employee=True)
    form = EventForm(_event_data(user, is_nda=True), user=user)
    assert form.is_valid(), form.errors
    assert form.save().is_nda is True


@pytest.mark.django_db
def test_event_form_community_moderator_cannot_change_existing_value(make_user):
    staff = make_user("staff", is_employee=True)
    contributor = make_user("contributor")
    event = Event.objects.create(name="Staff only", is_nda=False, created_by=staff)
    event.moderators.set([staff, contributor])

    form = EventForm(
        _event_data(
            contributor,
            name="Staff only",
            moderators=[staff.pk, contributor.pk],
            is_nda=True,
        ),
        instance=event,
        user=contributor,
    )
    assert form.is_valid(), form.errors
    assert form.save().is_nda is False


@pytest.mark.django_db
def test_event_form_no_longer_blocks_community_member_from_nda_events(make_user):
    """The old "only NDA members can create NDA events" rule is gone."""
    user = make_user("contributor")
    form = EventForm(_event_data(user, is_nda=True), user=user)
    assert form.is_valid(), form.errors
