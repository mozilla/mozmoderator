import json

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_GET

from mozilla_django_oidc.views import OIDCAuthenticationCallbackView

from moderator.moderate.models import Event, Question, Vote
from moderator.moderate.forms import QuestionForm


class OIDCCallbackView(OIDCAuthenticationCallbackView):
    def login_failure(self, msg=''):
        if not msg:
            msg = ('Login failed. Make sure you are using a valid email '
                   'address and you are a vouched Mozillian.')
        messages.error(self.request, msg)
        return super(OIDCCallbackView, self).login_failure()


def main(request):
    """Render main page."""
    if request.user.is_authenticated():
        events = Event.objects.filter(archived=False)
        return render(request, 'index.jinja', {
                               'events': events,
                               'user': request.user})
    else:
        return render(request, 'index.jinja', {'user': request.user})


@login_required(login_url='/')
def archive(request):
    """List of all archived events."""
    events_list = Event.objects.filter(archived=True)
    paginator = Paginator(events_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get('page')

    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    return render(request, 'archive.jinja', {'events': events})


@login_required(login_url='/')
def event(request, e_slug, q_id=None):
    """Render event questions."""
    event = Event.objects.get(slug=e_slug)
    question = None
    user = request.user
    if q_id:
        question = Question.objects.get(id=q_id)

    questions = (Question.objects.filter(event=event)
                 .annotate(vote_count=Count('votes'))
                 .order_by('-vote_count'))

    question_form = QuestionForm(request.POST or None,
                                 instance=question)

    is_reply = False
    if question_form.is_valid() and not event.archived:
        question_obj = question_form.save(commit=False)
        # Do not change the user if posting an reply
        if not question_obj.id:
            question_obj.asked_by = user
        elif not user.userprofile.is_admin:
            raise Http404
        else:
            is_reply = True
        question_obj.event = event
        question_obj.save()

        if not Vote.objects.filter(user=user, question=question_obj).exists() and not is_reply:
            Vote.objects.create(user=user, question=question_obj)

        return redirect(reverse('event', kwargs={'e_slug': event.slug}))

    return render(request, 'questions.jinja',
                  {'user': user,
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


@require_GET
def set_oidc_state(request):
    oidc_state = get_random_string(32)
    request.session['oidc_state'] = oidc_state
    return JsonResponse({'oidc_state': oidc_state})
