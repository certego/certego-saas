from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers as rfs

__all__ = [
    "ProductPriceSerializer",
    "InvoiceSerializer",
    "SubscriptionSerializer",
]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Example #1",
            response_only=True,
            value={
                "id": "prod_xyz",
                "name": "Researcher",
                "description": "50 submissions",
                "metadata": {
                    "max_submissions": "50",
                    "submission_type": "public",
                    "priority": "False",
                    "appname": "DRAGONFLY",
                },
                "currency": "usd",
                "unit_amount": 1500,
            },
        )
    ],
)
class ProductPriceSerializer(rfs.Serializer):
    """Represents a combination of
    :class:`stripe.Product` and :class:`stripe.Price`.
    """

    id = rfs.CharField()
    name = rfs.CharField()
    description = rfs.CharField()
    metadata = rfs.JSONField()
    currency = rfs.CharField()
    unit_amount = rfs.FloatField()


class InvoiceSerializer(rfs.Serializer):
    """
    Useful fields from :class:`stripe.Invoice`
    """

    # date-time
    created = rfs.IntegerField()
    due_date = rfs.IntegerField()
    period = rfs.SerializerMethodField()
    # monie
    total = rfs.FloatField()
    amount_due = rfs.FloatField()
    amount_paid = rfs.FloatField()
    amount_remaining = rfs.FloatField()
    # info
    status = rfs.CharField()
    currency = rfs.CharField()
    description = rfs.CharField()
    lines_descriptions = rfs.SerializerMethodField()
    # urls
    hosted_invoice_url = rfs.URLField()
    invoice_pdf = rfs.URLField()

    def get_period(self, obj) -> dict:
        try:
            return obj.lines.data[0].period
        except Exception:
            return {}

    def get_lines_descriptions(self, obj) -> list:
        try:
            return [line["description"] for line in obj["lines"]]
        except Exception:
            return []


class SubscriptionSerializer(rfs.Serializer):
    """
    Useful fields from
    :class:`stripe.Subscription` + custom fields
    """

    appname = rfs.CharField()
    status = rfs.CharField()
    current_period_start = rfs.IntegerField()
    current_period_end = rfs.IntegerField()
    days_until_due = rfs.IntegerField()
    start_date = rfs.IntegerField()
    created = rfs.IntegerField()
    ended_at = rfs.IntegerField()
    cancel_at = rfs.IntegerField()
    cancel_at_period_end = rfs.BooleanField()
    canceled_at = rfs.IntegerField()
    # custom fields
    product = ProductPriceSerializer()
    invoices = InvoiceSerializer(many=True)
