from django.urls import include, path

# Patterns
urlpatterns = [
    # certego_saas: user sub-app
    path("", include("certego_saas.user.urls")),
]
