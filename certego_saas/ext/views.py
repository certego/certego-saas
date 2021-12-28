"""
`DRF views <https://www.django-rest-framework.org/api-guide/views/>`__
"""

from rest_framework.views import APIView as _APIView


class APIView(_APIView):
    """
    Overrides DRF's ``APIView`` to always have ``get_serializer_context`` method.
    """

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(
            *args, **kwargs, context=self.get_serializer_context()
        )

    def get_serializer_context(self):
        """Extra context provided to the serializer class."""
        return {"request": self.request, "format": self.format_kwarg, "view": self}
