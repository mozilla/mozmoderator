from django.contrib import admin
from moderator.moderate.models import Event, Vote, Question


class QuestionInline(admin.StackedInline):
    model = Question
    readonly_fields = ('question', 'asked_by',)
    extra = 0


class EventAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('name', 'questions_count',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'asked_by', 'event')

admin.site.register(Event, EventAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Vote)
