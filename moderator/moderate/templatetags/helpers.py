import hashlib

import markdown
from django.utils.safestring import mark_safe
from django_jinja import library


@library.global_function
def user_voted(question, user):
    """Check if a user has already voted."""
    return question.votes.filter(user=user).exists()


@library.filter
def to_markdown(text):
    """Render markdown text to HTML."""
    md = markdown.Markdown(extensions=["fenced_code", "pymdownx.tilde"])
    return mark_safe(md.convert(text))


@library.global_function
def can_moderate_event(event, user):
    """Check if a user can moderate an event."""
    return user.is_superuser or event.moderators.filter(id=user.id).exists()


@library.global_function
def can_answer_question(question, user):
    """Check if a user can answer a question."""
    return not question.answer and can_moderate_event(question.event, user)


def get_gravatar_url(email, size=70, default="identicon"):
    if email:
        email_hash = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"
    return None


@library.global_function
def get_profile_image(user, is_anonymous=True):
    if user and not is_anonymous:
        return (
            get_gravatar_url(user.email)
            or user.userprofile.avatar_url
            or "/static/img/unknown.png"
        )
    return "/static/img/unknown.png"
