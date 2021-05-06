import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse

from moderator.moderate.models import Event, MozillianProfile, Question, Vote

# Unregister User from admin to attach MozillianProfile
admin.site.unregister(User)


def export_questions_csv(modeladmin, request, queryset):
    """Export questions csv."""
    filename = "questions.csv"
    response = HttpResponse(mimetype="text/csv")
    response["Content-Disposition"] = 'attachment; filename="%s"' % filename

    writer = csv.writer(response)

    for e in queryset:
        writer.writerow([e.name])
        questions = e.questions.annotate(vote_count=Count("votes")).order_by(
            "-vote_count"
        )
        for q in questions:
            writer.writerow([q.question.encode("utf-8"), q.votes.count()])

    return response


class MozillianProfileInline(admin.StackedInline):
    model = MozillianProfile
    fk_name = "user"


class UserAdmin(UserAdmin):
    inlines = [MozillianProfileInline]
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_nda_member",
        "is_staff",
    )
    search_fields = ["email", "first_name", "last_name"]

    def is_nda_member(self, obj):
        return obj.userprofile.is_nda_member

    is_nda_member.boolean = True


class QuestionInline(admin.StackedInline):
    model = Question
    fields = (
        "addressed",
        "question",
        "asked_by",
    )
    readonly_fields = (
        "question",
        "asked_by",
    )
    extra = 0


class EventAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = (
        "name",
        "questions_count",
        "created_at",
        "archived",
        "is_nda",
    )
    actions = [export_questions_csv]
    list_filter = ["archived"]
    autocomplete_fields = ["moderators"]


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "asked_by",
        "event",
        "question",
        "is_anonymous",
    )


admin.site.register(User, UserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote)
