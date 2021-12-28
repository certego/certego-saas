from django.db.models import Q
from rest_framework.viewsets import GenericViewSet

from .organization import Organization
from .permissions import (
    IsObjectOwnerOrSameOrgOrCertegoOrgPermission,
    IsObjectOwnerPermission,
)

__all__ = [
    "ObjectUserPermissionMixin",
    "ObjectUserQuerysetMixin",
    "ObjectUserPermissionQuerysetMixin",
]


class ObjectUserPermissionMixin(GenericViewSet):
    TO_RESTRICT_VIEW_ACTIONS = ["destroy", "partial_update", "update"]

    def get_permissions(self):
        permissions = super().get_permissions()
        if self.action in self.TO_RESTRICT_VIEW_ACTIONS:
            permissions.append(IsObjectOwnerPermission())
        else:
            permissions.append(IsObjectOwnerOrSameOrgOrCertegoOrgPermission())
        return permissions


class ObjectUserQuerysetMixin(GenericViewSet):
    TO_FILTER_VIEW_ACTIONS = ["list"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in self.TO_FILTER_VIEW_ACTIONS:
            user = self.request.user
            if user.has_membership():
                query = Q(user=user) | Q(
                    user__membership__organization_id__in=[
                        user.membership.organization_id,
                        Organization.certego().pk,
                    ]
                )
            else:
                query = Q(user=user) | Q(
                    user__membership__organization_id=Organization.certego().pk
                )
            queryset = queryset.filter(query)
        return queryset


class ObjectUserPermissionQuerysetMixin(
    ObjectUserPermissionMixin, ObjectUserQuerysetMixin
):
    pass
