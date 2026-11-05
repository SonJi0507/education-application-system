from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, BasePermission, IsAdminUser
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from apps.applications.mail import send_confirmation
from apps.applications.models import Application, ApplicationQuerySet
from apps.applications.serializers import ApplicationCreateSerializer, ApplicationStaffSerializer


class ApplicationPagination(PageNumberPagination):
    page_size = 20


class ApplicationViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    pagination_class = ApplicationPagination
    http_method_names = ("get", "post", "head", "options")

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self) -> type[BaseSerializer[Application]]:
        if self.action == "create":
            return ApplicationCreateSerializer
        return ApplicationStaffSerializer

    def get_queryset(self) -> ApplicationQuerySet:
        queryset = Application.objects.get_queryset().select_related("course")
        if self.action != "list":
            return queryset
        return queryset.filtered(
            status=self.request.query_params.get("status") or "",
            query=self.request.query_params.get("q") or "",
        )

    def perform_create(self, serializer: BaseSerializer[Application]) -> None:
        application = serializer.save()
        send_confirmation(application)
