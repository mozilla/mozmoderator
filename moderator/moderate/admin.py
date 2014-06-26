import csv

from django.db.models import Count
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse

from moderator.moderate.models import Event, MozillianProfile, Vote, Question


# Unregister User from admin to attach MozillianProfile
admin.site.unregister(User)


def export_questions_csv(modeladmin, request, queryset):
    """Export questions csv."""
    filename = 'questions.csv'
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = ('attachment; filename="%s"' %
                                       filename)

    writer = csv.writer(response)

    for e in queryset:
        writer.writerow([e.name])
        questions = (e.questions
                     .annotate(vote_count=Count('votes'))
                     .order_by('-vote_count'))
        for q in questions:
            writer.writerow([q.question.encode('utf-8'), q.votes.count()])

    return response


class MozillianProfileInline(admin.StackedInline):
    model = MozillianProfile
    fk_name = 'user'


class UserAdmin(UserAdmin):
    inlines = [MozillianProfileInline]


class QuestionInline(admin.StackedInline):
    model = Question
    readonly_fields = ('question', 'asked_by',)
    extra = 0


class EventAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('name', 'questions_count', 'archived')
    actions = [export_questions_csv]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'asked_by', 'event')


admin.site.register(User, UserAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote)
