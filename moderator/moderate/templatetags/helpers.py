from django import template

from moderator.moderate.models import Vote


register = template.Library()

@register.filter
def get_user_voted(user, question):
    return Vote.objects.filter(question=question, user=user).exists()
