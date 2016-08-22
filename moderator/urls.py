import session_csrf

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


session_csrf.monkeypatch()


urlpatterns = [
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # BrowserId
    url(r'', include('django_browserid.urls')),
    # Main landing page
    url(r'^', include('moderator.moderate.moderate_urls')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
