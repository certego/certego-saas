from certego_saas.settings import certego_apps_settings

# settings
STRIPE_LIVE_MODE = certego_apps_settings.STRIPE_LIVE_MODE
HOST_NAME = certego_apps_settings.HOST_NAME.lower()
CACHE_ALIAS = "certego_saas.payments"

# corresponding to products on stripe
PUBLIC_PRODUCT_NAME = "Public"
CERTEGO_USERS_PRODUCT_NAME = "Certego_Internal"

# for local development/testing
TEST_ADMIN_CUSTOMER_ID = "cus_KHkAVst4QtdUow"
TEST_ADMIN_DF_SUBSCRIPTION_ID = "sub_1JyZeuFdd9yl5D0d24Wb0f4r"
TEST_ADMIN_DF_PRODUCT_ID = "prod_KHjKIZ2FJHKHrk"
TEST_ADMIN_IO_PRODUCT_ID = "prod_KteBrO2aApO5pS"


# webhook
STRIPE_WEBHOOK_SIGNING_KEY = certego_apps_settings.STRIPE_WEBHOOK_SIGNING_KEY

# logging
STRIPE_SENSITIVE_FIELDS_SET = {
    # customer
    "default_payment_method",
    "default_source",
    "sources",
    "address",
    "phone",
    "shipping",
    # susbcription
    "customer_address",
    "customer_phone",
    "customer_shipping",
    # invoice
    "lines",
    "hosted_invoice_url",
    "invoice_pdf",
    "invoice_settings",
    "invoice_prefix",
    # extra
    "items",
}
