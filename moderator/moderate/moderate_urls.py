from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()

urlpatterns = patterns(
    '',
    # Events questions urls
    url(r'^e/(?P<e_slug>[a-z0-9-]+)', 'moderator.moderate.views.event',
        name='event'),
    # Question upvote
    url(r'^q/(?P<q_id>\d+)/upvote', 'moderator.moderate.views.upvote',
        name='upvote'),
    # Main landing page
    url(r'^$', 'moderator.moderate.views.main', name='main'),
    # Archive page
    url(r'^archives$', 'moderator.moderate.views.archive', name='archive'),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
