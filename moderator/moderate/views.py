from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.http import Http404, JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from mozilla_django_oidc.views import OIDCAuthenticationCallbackView

from moderator.moderate.forms import EventForm, QuestionForm
from moderator.moderate.models import Event, Question, Vote


class OIDCCallbackView(OIDCAuthenticationCallbackView):
    """Override OIDC callback view."""

    def login_failure(self, msg=""):
        """Returns a custom message in case of login failure."""

        if not msg:
            msg = "Login failed. Access is allowed only to staff and NDA members."
        messages.error(self.request, msg)
        return super(OIDCCallbackView, self).login_failure()


def main(request):
    """Render main page."""
    user = request.user
    if user.is_authenticated:

        events = Event.objects.filter(archived=False)
        if not user.userprofile.is_nda_member:
            events = events.exclude(is_nda=True)
        return render(request, "index.jinja", {"events": events, "user": user})
    return render(request, "index.jinja", {"user": user})


@login_required(login_url="/")
def archive(request):
    """List of all archived events."""
    q_args = {
        "archived": True,
    }
    # Filter out NDA events for non-NDA users
    if not request.user.userprofile.is_nda_member and not request.user.is_superuser:
        q_args["is_nda"] = False
    events_list = Event.objects.filter(**q_args)
    paginator = Paginator(events_list, settings.ITEMS_PER_PAGE)
    page = request.GET.get("page")

    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    return render(request, "archive.jinja", {"events": events})


@login_required(login_url="/")
def edit_event(request, slug=None):
    """Creates a new event."""
    user = request.user
    query_args = {"created_by": user}
    if slug:
        query_args["slug"] = slug

    if user.is_superuser:
        del query_args["created_by"]

    event = get_object_or_404(Event, **query_args) if slug else None
    event_form = EventForm(request.POST or None, instance=event, user=user)

    if event_form.is_valid():
        e = event_form.save(commit=False)
        if not event:
            e.created_by = user
        e.save()

        if slug:
            msg = "Event successfully edited."
        else:
            msg = "Event successfully created."
        messages.success(request, msg)
        return redirect(reverse("main"))

    ctx = {
        "slug": event.slug if event else None,
        "event_form": event_form,
        "event": event,
        "profile": user.userprofile,
    }

    return render(request, "create_event.jinja", ctx)


@login_required(login_url="/")
def delete_event(request, slug):
    """Delete an event."""
    user = request.user
    query_args = {"slug": slug, "created_by": user}
    # Allow superusers to edit all events
    if user.is_superuser:
        del query_args["created_by"]

    event = get_object_or_404(Event, **query_args)
    event.delete()
    msg = "Event successfully deleted."
    messages.success(request, msg)
    return redirect(reverse("main"))


@login_required(login_url="/")
def show_event(request, e_slug, q_id=None):
    """Render event questions."""
    event = get_object_or_404(Event, slug=e_slug)
    question = None
    user = request.user

    # Do not display NDA events to non NDA members or non employees.
    if event.is_nda and not user.userprofile.is_nda_member:
        raise Http404

    if q_id:
        question = Question.objects.get(id=q_id)

    questions_q = Question.objects.filter(event=event).annotate(
        vote_count=Count("votes")
    )
    if user.userprofile.is_admin:
        questions = questions_q.order_by("-vote_count")
    else:
        questions = questions_q.order_by("?")

    question_form = QuestionForm(request.POST or None, instance=question)

    is_replied = False
    if question_form.is_valid() and not event.archived:
        question_obj = question_form.save(commit=False)
        # Do not change the user if posting a reply
        if not question_obj.id:
            if not question_obj.is_anonymous:
                question_obj.asked_by = user
        elif not user.userprofile.is_admin:
            raise Http404
        else:
            is_replied = True
        question_obj.event = event
        question_obj.save()

        if (
            not Vote.objects.filter(user=user, question=question_obj).exists()
            and not is_replied
        ):
            Vote.objects.create(user=user, question=question_obj)

        return redirect(reverse("event", kwargs={"e_slug": event.slug}))

    return render(
        request,
        "questions.jinja",
        {
            "user": user,
            "open": not event.archived,
            "event": event,
            "questions": questions,
            "q_form": question_form,
        },
    )


@login_required
def upvote(request, q_id):
    """Upvote question"""

    question = Question.objects.get(pk=q_id)
    user_can_vote = True
    user = request.user
    if question.event.is_nda and not user.userprofile.is_nda_member:
        user_can_vote = False

    if request.is_ajax() and not question.event.archived and user_can_vote:
        if not Vote.objects.filter(user=user, question=question).exists():
            Vote.objects.create(user=user, question=question)
        else:
            Vote.objects.filter(user=user, question=question).delete()

        response_dict = {"current_vote_count": question.votes.count()}

        return JsonResponse(response_dict)

    return show_event(request, question.event.slug)


def login_local_user(request, username=""):
    """Allow a user to login for local dev."""
    if not (settings.DEV and settings.ENABLE_DEV_LOGIN) or not username:
        raise Http404

    user = None
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404

    if user:
        auth.login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return HttpResponseRedirect(reverse("main"))
