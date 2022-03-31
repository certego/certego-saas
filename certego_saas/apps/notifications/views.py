import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from certego_saas.ext.viewsets import ReadOnlyViewSet
from certego_saas.settings import certego_apps_settings

from .filters import NotificationFilter
from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)

__all__ = [
    "NotificationViewSet",
]


class NotificationViewSet(ReadOnlyViewSet):
    queryset = Notification.objects.order_by("-created_at")
    serializer_class = NotificationSerializer
    filter_class = NotificationFilter

    def get_queryset(self):
        qs = super().get_queryset()
        # if FILTER_NOTIFICATIONS_VIEW_FOR_CURRENTAPP is True then,
        # filter notifications queryset using `AppChoices.CURRENTAPP`.
        if certego_apps_settings.FILTER_NOTIFICATIONS_VIEW_FOR_CURRENTAPP:
            qs = qs.filter_currentapp()
        return qs

    @action(
        url_path="mark-as-read",
        detail=True,
        methods=["POST"],
        url_name="mark_as_read",
    )
    def mark_as_read(self, request: Request, *args, **kwargs):
        logger.info(f"mark as read notification from user: {request.user}")
        obj: Notification = self.get_object()
        obj.read_by_users.add(request.user)  # type: ignore
        return Response(status=status.HTTP_204_NO_CONTENT)
