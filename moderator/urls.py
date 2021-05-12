from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from mozilla_django_oidc import urls as django_oidc_urls

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Django OIDC authentication urls
    path("oidc/", include(django_oidc_urls)),
    # Main landing page
    path("", include("moderator.moderate.moderate_urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

if settings.SHOW_DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
