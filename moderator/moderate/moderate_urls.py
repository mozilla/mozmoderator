from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^e/(?P<e_slug>[a-z0-9-]+)$', 'moderator.moderate.views.event',
        name='event'),
    url(r'^e/(?P<e_slug>[a-z0-9-]+)/q/(?P<q_id>\d+)$',
        'moderator.moderate.views.event', name='reply'),
    url(r'^q/(?P<q_id>\d+)/upvote', 'moderator.moderate.views.upvote',
        name='upvote'),
    url(r'^$', 'moderator.moderate.views.main', name='main'),
    url(r'^archives$', 'moderator.moderate.views.archive', name='archive'),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
