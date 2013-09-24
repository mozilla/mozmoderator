from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()

urlpatterns = patterns('',

    # BrowserId
    url(r'^browserid/', include('django_browserid.urls'),
        name='mozilla_browserid_verify'),

    # Login/Logout
    url(r'^login/failed/$', 'moderator.moderate.views.login_failed',
        name='login_failed'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # Main landing page
    url(r'^$', 'moderator.moderate.views.main', name='main'),

    # Events questions urls
    url(r'^e/(?P<e_slug>[a-z0-9-]+)', 'moderator.moderate.views.event',
        name='event'),

    # Question upvote
    url(r'^q/(?P<q_id>\d+)/upvote', 'moderator.moderate.views.upvote',
        name='upvote'),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
