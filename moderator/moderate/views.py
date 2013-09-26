from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django_browserid import get_audience, verify
from django_browserid.views import Verify
from django_browserid.auth import default_username_algo
from django.shortcuts import redirect, render
from django.utils import simplejson
from django.http import HttpResponse

from moderator.moderate.mozillians import is_vouched, BadStatusCodeError
from moderator.moderate.models import MozillianProfile, Event, Question, Vote
from moderator.moderate.forms import QuestionForm


class CustomVerify(Verify):
    def form_valid(self, form):
        if form.is_valid():
            self.assertion = form.cleaned_data['assertion']
            self.audience = get_audience(self.request)
            result = verify(self.assertion, self.audience)
            try:
                _is_valid_login = False
                if result:
                    if User.objects.filter(email=result['email']).exists():
                        _is_valid_login = True
                    else:
                        data = is_vouched(result['email'])
                        if data and data['is_vouched']:
                            _is_valid_login = True
                            user = User.objects.create_user(
                                username=default_username_algo(data['email']),
                                email=data['email'])
                            user.save()
                            mozillian = MozillianProfile(
                                user=user,
                                username=data['username'],
                                avatar_url=data['photo'])
                            mozillian.save()

                if _is_valid_login:
                    user = auth.authenticate(assertion=self.assertion,
                                             audience=self.audience)
                    auth.login(self.request, user)
                    return redirect('main')

            except BadStatusCodeError:
                message = ('Login failed.')
                return login_failed(self.request, message)

        return login_failed(self.request)


def login_failed(request, msg=None):
    """Login failed view.

    This view acts like a segway between a failed login attempt and
    'main' view. Adds messages in the messages framework queue, that
    informs user login failed.

    """
    if not msg:
        msg = ('Login failed.')
    messages.warning(request, msg)

    return render(request, 'index.html', {'user': request.user})


def main(request):
    """Render main page."""
    if request.user.is_authenticated():
        events = Event.objects.all()
        return render(request, 'index.html', {
            'events': events,
            'user': request.user
            })
    else:
        return login_failed(request)


@login_required
def event(request, e_slug):
    """Render event questions."""
    event = Event.objects.get(slug=e_slug)
    questions = Question.objects.filter(event=event)
    question_form = QuestionForm(request.POST or None)

    if question_form.is_valid():
        question = question_form.save(commit=False)
        question.asked_by = request.user
        question.event = event
        question.save()

        # After succesful save provide clean question form
        question_form = QuestionForm()

    return render(request, 'questions.html',
                  {'user': request.user,
                   'event': event,
                   'questions': questions,
                   'q_form': question_form})


@login_required
def upvote(request, q_id):
    """Upvote question"""

    question = Question.objects.get(pk=q_id)

    if request.is_ajax():
        vote, created = Vote.objects.get_or_create(user=request.user,
                                                   question=question)

        response_dict = {}
        response_dict.update({'current_vote_count': question.get_vote_count})

        return HttpResponse(simplejson.dumps(response_dict),
                            mimetype='application/javascript')

    return event(request, question.event.slug)
