from django.urls import path

from .views import UserAccessView

urlpatterns = [
    path(
        "me/access",
        UserAccessView.as_view(),
        name="user_access",
    ),
]
