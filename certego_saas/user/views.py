from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from certego_saas.ext.serializers import APIExceptionSerializer
from certego_saas.ext.views import APIView

from ..settings import certego_apps_settings

UserAccessSerializer = certego_apps_settings.USER_ACCESS_SERIALIZER

__all__ = [
    "UserAccessView",
]


@extend_schema(
    description="""
    Returns user's access information.
    """,
    responses={
        200: UserAccessSerializer,
        500: APIExceptionSerializer,
    },
)
class UserAccessView(APIView):
    serializer_class = UserAccessSerializer

    def get(self, request, *args, **kwargs):
        # make sure there's corresponding customer object
        user = request.user
        # get user access info and serialize it
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data)
