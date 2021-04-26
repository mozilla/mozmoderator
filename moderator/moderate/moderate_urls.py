from django.conf import settings
from django.conf.urls import include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from moderator.moderate import views as moderate_views

event_urls = [
    path("<str:e_slug>/", moderate_views.show_event, name="event"),
    path("<str:e_slug>/q/<int:q_id>", moderate_views.show_event, name="reply"),
    path("<str:slug>/edit", moderate_views.edit_event, name="edit_event"),
    path("<str:slug>/delete", moderate_views.delete_event, name="delete_event"),
]

question_urls = [
    path("<str:q_id>/upvote", moderate_views.upvote, name="upvote"),
]

urlpatterns = [
    path("", moderate_views.main, name="main"),
    path("archives", moderate_views.archive, name="archive"),
    path("event/new", moderate_views.edit_event, name="create_event"),
    path("e/", include(event_urls)),
    path("q/", include(question_urls)),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

if settings.DEV and settings.ENABLE_DEV_LOGIN:
    urlpatterns += [
        path(
            "u/<str:username>/login", moderate_views.login_local_user, name="dev_login"
        )
    ]
