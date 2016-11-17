import session_csrf

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from mozilla_django_oidc import urls as django_oidc_urls

session_csrf.monkeypatch()


urlpatterns = [
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # Django OIDC authentication urls
    url(r'oidc/', include(django_oidc_urls)),
    # Main landing page
    url(r'^', include('moderator.moderate.moderate_urls')),
    # contribute.json url
    url(r'^(?P<path>contribute\.json)$', 'django.views.static.serve',
        {'document_root': settings.ROOT})
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
