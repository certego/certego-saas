import csv
from typing import Dict

from django.http import HttpResponse
from rest_framework.generics import GenericAPIView

from .serializers import RecaptchaV2Serializer


class ExportCsvAdminMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"  # type: ignore


class SerializerActionMixin(GenericAPIView):
    """
    Define mapping in ``serializer_action_classes`` (``dict``).
    """

    serializer_action_classes: Dict = {}

    def get_serializer_class(self, *args, **kwargs):
        """
        Instantiate the list of serializers per action from class attribute
        (must be defined).
        """
        kwargs["partial"] = True
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(SerializerActionMixin, self).get_serializer_class()


class RecaptchaV2Mixin(GenericAPIView):
    """
    Mixin that hooks the ``RecaptchaV2Serializer`` into ``get_serializer()``.
    The hook is applied only if ``self.request.method`` is ``POST``.
    """

    def get_serializer(self, *args, **kwargs):
        if self.request.method == "POST":
            # first validate against the recaptcha serializer
            recaptcha_serializer = RecaptchaV2Serializer(
                data=self.request.data, context=self.get_serializer_context()
            )
            recaptcha_serializer.is_valid(raise_exception=True)
        return super().get_serializer(*args, **kwargs)
