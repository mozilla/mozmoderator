from django_jinja import library


@library.global_function
def user_voted(question, user):
    """Check if a user has already voted."""
    return question.votes.filter(user=user).exists()
