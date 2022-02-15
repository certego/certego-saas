from drf_spectacular.utils import extend_schema

from certego_saas.ext.throttling import POSTUserRateThrottle
from certego_saas.ext.viewsets import CreateOnlyViewSet

from .models import UserFeedback
from .serializers import UserFeedbackSerializer


@extend_schema(
    description="""
    Authenticated users can submit feedback by POSTing to this endpoint.
    """,
)
class UserFeedbackCreateViewSet(CreateOnlyViewSet):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    throttle_classes = [POSTUserRateThrottle]
