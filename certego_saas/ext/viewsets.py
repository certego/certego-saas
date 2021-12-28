"""
`DRF viewsets <https://www.django-rest-framework.org/api-guide/viewsets/>`__
"""

from rest_framework import mixins, viewsets

from .throttling import (
    DELETEModelUserRateThrottle,
    PATCHModelUserRateThrottle,
    POSTModelUserRateThrottle,
)


class ReadOnlyViewSet(
    viewsets.ReadOnlyModelViewSet,
):
    """
    Only ``list()`` and ``retrieve()`` actions.
    """


class CreateOnlyViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Only ``create()`` action.
    """

    throttle_classes = [
        POSTModelUserRateThrottle,
    ]


class ListAndDeleteOnlyViewSet(
    mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    Only ``list()`` and ``destroy()`` actions.
    """

    throttle_classes = [
        DELETEModelUserRateThrottle,
    ]


class ReadAndDeleteOnlyViewSet(
    mixins.DestroyModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """
    Only ``list()``, ``retrieve()``, and ``destroy()`` actions.
    """

    throttle_classes = [
        DELETEModelUserRateThrottle,
    ]


class ReadDeleteCreateOnlyViewSet(
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.ReadOnlyModelViewSet,
):
    """
    Only ``list()``, ``retrieve()``, ``destroy()`` and ``create()`` actions.
    """

    throttle_classes = [
        POSTModelUserRateThrottle,
        DELETEModelUserRateThrottle,
    ]


class ReadUpdateCreateOnlyViewSet(
    mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet
):
    throttle_classes = [
        POSTModelUserRateThrottle,
        PATCHModelUserRateThrottle,
    ]
