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
