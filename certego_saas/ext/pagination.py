from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

__all__ = [
    "CustomPageNumberPagination",
]

""" Pagination """


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        paginate = request.query_params.get("paginate", "true") != "false"
        if paginate:
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
