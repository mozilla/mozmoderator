import json

from django_browserid.auth import default_username_algo
from django_browserid.base import (BrowserIDException, RemoteVerifier,
                                   get_audience)
from django_browserid.views import Verify

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect


from moderator.moderate.mozillians import is_vouched, BadStatusCodeError
from moderator.moderate.models import Event, Question, Vote
from moderator.moderate.forms import QuestionForm


class BrowserIDVerify(Verify):

    def login_failure(self, msg=''):
        if msg:
            messages.warning(self.request, msg)
        return super(BrowserIDVerify, self).login_failure()

    def post(self, *args, **kwargs):
        """Custom mozillians login form validation"""
        msg = ('Login failed. Please make sure you are using a valid email '
               'address and you are a vouched Mozillian.')
        assertion = self.request.POST.get('assertion')

        if not assertion:
            return self.login_failure(msg)
        audience = get_audience(self.request)
        result = RemoteVerifier().verify(assertion, audience)

        if not result:
            return self.login_failure(msg)

        email = result.email
        _is_valid_login = False
        if User.objects.filter(email=email).exists():
            _is_valid_login = True
        else:
            try:
                data = is_vouched(email)
            except BadStatusCodeError:
                msg = ('Email (%s) authenticated but was unable to connect to '
                       'Mozillians to see if you are vouched')
                return self.login_failure(msg)

            if data and data['is_vouched']:
                _is_valid_login = True
                user = User.objects.create_user(
                    username=default_username_algo(data['email']),
                    email=data['email'])
                profile = user.userprofile
                profile.username = data['username']
                profile.avatar_url = data['photo']
                profile.save()

        if _is_valid_login:
            try:
                self.user = auth.authenticate(assertion=assertion,
                                              audience=audience)
                auth.login(self.request, self.user)

            except BrowserIDException:
                return self.login_failure(msg)

            if self.user and self.user.is_active:
                return super(BrowserIDVerify, self).login_success()
        return self.login_failure(msg)


def main(request):
    """Render main page."""
    if request.user.is_authenticated():
        events = Event.objects.filter(archived=False)
        return render(request, 'index.html', {
                               'events': events,
                               'user': request.user})
    return render(request, 'index.html', {'user': request.user})


@login_required(login_url='/')
def archive(request):
    """List of all archived events."""
    events_list = Event.objects.all()
    paginator = Paginator(events_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    return render(request, 'archive.html', {'events': events})


@login_required(login_url='/')
def event(request, e_slug):
    """Render event questions."""
    event = Event.objects.get(slug=e_slug)

    questions = (Question.objects.filter(event=event)
                 .annotate(vote_count=Count('votes'))
                 .order_by('-vote_count'))

    question_form = None
    if not event.archived:
        question_form = QuestionForm(request.POST or None)

    if question_form and question_form.is_valid():
        question = question_form.save(commit=False)
        question.asked_by = request.user
        question.event = event
        question.save()

        Vote.objects.create(user=request.user, question=question)

        return redirect(reverse('event', kwargs={'e_slug': event.slug}))

    return render(request, 'questions.html',
                  {'user': request.user,
                   'open': not event.archived,
                   'event': event,
                   'questions': questions,
                   'q_form': question_form})


@login_required
def upvote(request, q_id):
    """Upvote question"""

    question = Question.objects.get(pk=q_id)

    if request.is_ajax() and not question.event.archived:
        try:
            Vote.objects.create(user=request.user, question=question)
            status = 'unsupport'
        except IntegrityError:
            Vote.objects.filter(user=request.user, question=question).delete()
            status = 'support'

        response_dict = {
            'current_vote_count': question.votes.count(),
            'status': status,
        }

        return HttpResponse(json.dumps(response_dict),
                            mimetype='application/json')

    return event(request, question.event.slug)
