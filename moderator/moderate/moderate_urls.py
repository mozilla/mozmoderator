from django.conf import settings
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from moderator.moderate import views as moderate_views

urlpatterns = [
    url(r'^e/(?P<e_slug>[a-z0-9-]+)$', moderate_views.event, name='event'),
    url(r'^e/(?P<e_slug>[a-z0-9-]+)/q/(?P<q_id>\d+)$', moderate_views.event, name='reply'),
    url(r'^q/(?P<q_id>\d+)/upvote', moderate_views.upvote, name='upvote'),
    url(r'^$', moderate_views.main, name='main'),
    url(r'^archives$', moderate_views.archive, name='archive'),
    url(r'^set_oidc_state$', moderate_views.set_oidc_state, name='set_oidc_state')
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
