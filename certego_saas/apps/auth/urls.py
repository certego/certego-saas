from django.urls import path

from .views import LoginView, LogoutView

urlpatterns = [
    # durin + Custom Auth APIs
    path("login", LoginView.as_view(), name="auth_login"),
    path("logout", LogoutView.as_view(), name="auth_logout"),
]
