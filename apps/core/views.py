import structlog
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.health import dependency_health
from config.api.renderers import StructuredJSONRenderer

logger = structlog.getLogger()


@extend_schema(exclude=True)
class LivenessAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        return Response(data={"status": "ok"}, status=status.HTTP_200_OK)


@extend_schema(exclude=True)
class ReadinessAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        dependencies = dependency_health()
        is_ready = all(dependencies.values())

        if not is_ready:
            logger.warning("application_not_ready", dependencies=dependencies)

        return Response(
            data={
                "status": "ok" if is_ready else "unavailable",
                "dependencies": dependencies,
            },
            status=(
                status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )


@extend_schema(exclude=True)
class APIRootAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    renderer_classes = [StructuredJSONRenderer, TemplateHTMLRenderer]

    def get(self, request: HttpRequest) -> HttpResponse:
        data = {
            "name": "Choto API",
            "version": "v1",
            "status": "ok",
            "endpoints": {
                "Docs": request.build_absolute_uri(reverse("swagger-ui")),
                "Health": request.build_absolute_uri(reverse("core:health-live")),
                "Auth": request.build_absolute_uri(reverse("token_obtain_pair")),
                "Short links": request.build_absolute_uri(reverse("links:list-create")),
                "Subscription": request.build_absolute_uri(
                    reverse("billing:subscription-detail")
                ),
                "Webhooks": request.build_absolute_uri(
                    reverse("webhooks:endpoint-list-create")
                ),
            },
        }

        if isinstance(request.accepted_renderer, TemplateHTMLRenderer):
            return Response(data, template_name="core/api_root.html")

        return Response(data)
