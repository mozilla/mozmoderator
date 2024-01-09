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
    md = markdown.Markdown(extensions=["fenced_code"])
    return mark_safe(md.convert(text))
