from django.urls import include, path
from rest_framework import routers

from .views import UserFeedbackCreateViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"give_feedback", UserFeedbackCreateViewSet, basename="user_feedback")

urlpatterns = [
    path("", include(router.urls)),
]
