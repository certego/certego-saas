"""
`DRF serializers <https://www.django-rest-framework.org/api-guide/serializers/>`__
"""

from drf_recaptcha.fields import ReCaptchaV2Field
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers as rfs

__all__ = [
    "APIExceptionSerializer",
]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Generic Example",
            response_only=True,
            value={"errors": "Failed to fetch. Please try again later."},
        )
    ],
)
class APIExceptionSerializer(rfs.Serializer):
    errors = rfs.JSONField()  # type: ignore


class RecaptchaV2Serializer(rfs.Serializer):
    recaptcha = ReCaptchaV2Field()
