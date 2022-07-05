from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from certego_saas.ext.mixins import ExportCsvAdminMixin

from .forms import UserCreateForm


class AbstractUserAdmin(DjangoUserAdmin, ExportCsvAdminMixin):
    """
    An abstract admin class for the
    :class:`certego_saas.user.models.User` model.
    """

    add_form = UserCreateForm
    prepopulated_fields = {
        "username": (
            "first_name",
            "last_name",
        )
    }
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "approved",
        "is_staff",
    )
    list_filter = (
        "is_active",
        "approved",
        "is_staff",
        "is_superuser",
        "groups",
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
