from django.conf import settings
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from moderator.moderate import views as moderate_views

urlpatterns = [
    url(r'^e/(?P<e_slug>[a-z0-9-]+)$', moderate_views.show_event, name='event'),
    url(r'^e/(?P<e_slug>[a-z0-9-]+)/q/(?P<q_id>\d+)$', moderate_views.show_event, name='reply'),
    url(r'^q/(?P<q_id>\d+)/upvote', moderate_views.upvote, name='upvote'),
    url(r'^$', moderate_views.main, name='main'),
    url(r'^archives$', moderate_views.archive, name='archive'),
    url(r'^event/new$', moderate_views.edit_event, name='create_event'),
    url(r'^e/(?P<slug>[a-z0-9-]+)/edit$', moderate_views.edit_event, name='edit_event'),
    url(r'^e/(?P<slug>[a-z0-9-]+)/delete$', moderate_views.delete_event, name='delete_event'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
