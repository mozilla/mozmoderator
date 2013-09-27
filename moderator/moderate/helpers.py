from jingo import register


@register.function
def user_voted(question, user):
    """Check if a user has already voted."""
    return question.vote_set.filter(user=user).exists()
