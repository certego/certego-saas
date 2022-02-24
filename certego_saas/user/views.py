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
    """
    This is supposed to be the first endpoint hit
    by the user when they visit the webapp.
    Ideally, it should respond with user information,
    user usage information and user subscription information.

    This view's ``serializer_class`` is populated using the
    ``USER_ACCESS_SERIALIZER`` settings variable.
    """

    serializer_class = UserAccessSerializer

    def get(self, request, *args, **kwargs):
        # make sure there's corresponding customer object
        user = request.user
        # get user access info and serialize it
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data)
