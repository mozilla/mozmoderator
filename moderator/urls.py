from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()

urlpatterns = patterns('',
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # BrowserId
    url(r'', include('moderator.moderate.moderate_urls')),
    # Login / Logout
    url(r'^login/failed/$', 'moderator.moderate.views.login_failed',
        name='login_failed'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),
    # Main landing page
    url(r'^$', include('moderator.moderate.moderate_urls')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
