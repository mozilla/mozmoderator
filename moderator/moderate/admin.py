from django.contrib import admin
from moderator.moderate.models import Event, Vote, Question

admin.site.register(Event)
admin.site.register(Vote)
admin.site.register(Question)
