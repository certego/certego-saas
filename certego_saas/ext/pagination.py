"""
`DRF pagination <https://www.django-rest-framework.org/api-guide/pagination/>`__
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

__all__ = [
    "CustomPageNumberPagination",
]


class CustomPageNumberPagination(PageNumberPagination):
    """
    Extends DRF's ``PageNumberPagination`` to allow dynamic toggling
    of pagination using a query parameter
    called ``paginate`` that takes boolean input (default ``true``).
    """

    default_paginate = True
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        paginate_str = request.query_params.get(
            "paginate", str(self.default_paginate).lower()
        )
        if paginate_str != "false":
            return super(CustomPageNumberPagination, self).paginate_queryset(
                queryset, request, view=view
            )
        return None

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "total_pages": {
                    "type": "integer",
                    "example": 5,
                },
                "results": schema,
            },
        }
