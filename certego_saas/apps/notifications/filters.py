import rest_framework_filters as filters
from django.db.models import Value

from .models import Notification

__all__ = ["NotificationFilter"]


class NotificationFilter(filters.FilterSet):
    """
    Used in :class:`~.views.NotificationViewSet`.
    """

    read = filters.BooleanFilter(method="filter_for_read")

    def filter_for_read(self, queryset, value, read, *args, **kwargs):
        if read is True:
            return queryset.filter(read_by_users__in=[self.request.user]).annotate(
                read=Value(True)
            )
        if read is False:
            return queryset.exclude(read_by_users__in=[self.request.user]).annotate(
                read=Value(False)
            )
        return queryset

    class Meta:
        model = Notification
        fields = ["read"]
