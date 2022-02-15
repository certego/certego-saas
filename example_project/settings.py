import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "averysecurerandomsecret"

DEBUG = True
PUBLIC_DEPLOYMENT = True
STAGE_PRODUCTION = False
STAGE = "ci"
STAGE_LOCAL = False
STAGE_CI = True
HOST_URI = "http://localhost"
HOST_NAME = "ExampleProject"

ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    # default
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # extra
    "rest_framework",
    "rest_framework_filters",
    "drf_spectacular",
    # project apps (certego libs)
    "durin",
    "certego_saas",
    "certego_saas.apps.feedback",
    "certego_saas.apps.notifications",
    "certego_saas.apps.organization",
    "certego_saas.apps.payments",
]
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "certego_saas.ext.middlewares.StatsMiddleware",  # certego.ext
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "certego_saas.templates.context_processors.host",  # certego.ext
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
ROOT_URLCONF = "example_project.urls"
WSGI_APPLICATION = "example_project.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = "/static/"

AUTH_USER_MODEL = "certego_saas.User"

# certego_saas

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": "/tmp/dj_cache_example_project",
    },
    "certego_saas.payments": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        "LOCATION": "/tmp/dj_cache_example_project",
        "KEY_PREFIX": "certego_saas.payments",
    },
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # Auth
    "DEFAULT_AUTHENTICATION_CLASSES": ["durin.auth.TokenAuthentication"],
    # Pagination
    "DEFAULT_PAGINATION_CLASS": "certego_saas.ext.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
    # Permission
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # Exception Handling
    "EXCEPTION_HANDLER": "certego_saas.ext.exceptions.custom_exception_handler",
    # Filter
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework_filters.backends.RestFrameworkFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

REST_DURIN = {
    "USER_SERIALIZER": "certego_saas.user.serializers.UserSerializer",
    "REFRESH_TOKEN_ON_LOGIN": True,
    "API_ACCESS_CLIENT_NAME": "Example project API",
    "API_ACCESS_EXCLUDE_FROM_SESSIONS": True,
    "API_ACCESS_RESPONSE_INCLUDE_TOKEN": True,
}

CERTEGO_SAAS = {
    "ORGANIZATION_MAX_MEMBERS": 5,
}
