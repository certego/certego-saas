from django.contrib import admin

from .models import Customer, Subscription

__all__ = [
    "CustomerAdmin",
]

# Register sites!


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Django's ModelAdmin for ``Customer``.
    """

    list_display = (
        "customer_id",
        "user",
        "currentapp_subscription",
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Django's ModelAdmin for ``Subscription``.
    """

    list_display = (
        "subscription_id",
        "customer",
        "appname",
        "product_name",
    )
