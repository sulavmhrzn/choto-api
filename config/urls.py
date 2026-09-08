from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenVerifyView,
)

from apps.accounts.views import CustomTokenObtainPairAPIView, CustomTokenRefreshAPIView
from apps.links.views import ShortLinkRedirectAPIView

urlpatterns = [
    path("admin-tipbba/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("prometheus/", include("django_prometheus.urls")),
    path("api/v1/accounts/", include("apps.accounts.urls")),
    path("api/v1/links/", include("apps.links.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/webhooks/", include("apps.webhooks.urls")),
    path(
        "api/v1/auth/token/",
        CustomTokenObtainPairAPIView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/v1/auth/token/refresh/",
        CustomTokenRefreshAPIView.as_view(),
        name="token_refresh",
    ),
    path("api/v1/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v1/billing/", include("apps.billing.urls")),
    path("auth/", include("allauth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "<str:short_code>/",
        ShortLinkRedirectAPIView.as_view(),
        name="short-link-redirect",
    ),
]
