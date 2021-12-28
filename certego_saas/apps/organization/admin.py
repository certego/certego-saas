from django.contrib import admin

from .invitation import Invitation
from .membership import Membership
from .organization import Organization


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "organization",
        "is_owner",
        "created_at",
    )

    list_filter = (
        "organization",
        "is_owner",
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "members_count", "created_at")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "user",
        "organization",
        "created_at",
    )

    list_filter = (
        "status",
        "organization",
    )
