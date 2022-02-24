from typing import Dict, List

import stripe

from certego_saas.ext.models import AppChoices

from .cache import cache_memoize
from .consts import CERTEGO_USERS_PRODUCT_NAME, PUBLIC_PRODUCT_NAME, STRIPE_LIVE_MODE


@cache_memoize(60 * 60 * 24)
def get_products() -> List[Dict]:
    """
    Returns list of stripe plans/products.

    Alias for ``stripe.Price.list(expand=["data.product"])``.
    """
    prices = stripe.Price.list(expand=["data.product"]).data
    prod_price_list = []
    for price in prices:
        product = price.product
        if product.name == "Integration":
            continue  # skip to next iteration
        if product.active:
            prod_price_list.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "metadata": product.metadata,
                    "currency": price.currency,
                    "unit_amount": price.unit_amount,
                }
            )

    return prod_price_list


@cache_memoize(60 * 60 * 24)
def get_products_prices_map() -> Dict[str, Dict]:
    """
    Returns dict mapping of stripe plans/products.

    Alias for ``stripe.Price.list(expand=["data.product"])``.
    """
    prices = stripe.Price.list(expand=["data.product"]).data
    product_price_map = {}
    for price in prices:
        price_id = price.id
        product_id = price.product.id
        product_name = price.product.name
        appname = price.product.metadata["appname"]
        obj = {
            "id": product_id,
            "price_id": price_id,
            "name": product_name,
            "metadata": price.product.metadata,
        }
        product_price_map[price_id] = obj
        product_price_map[product_id] = obj
        product_price_map[f"{product_name}__{appname}"] = obj

    return product_price_map


def get_default_product() -> dict:
    """
    returns default product based on
    whether stripe is running in livemode or testmode
    """

    if STRIPE_LIVE_MODE:
        # public deployment
        name = f"{PUBLIC_PRODUCT_NAME}__{AppChoices.CURRENTAPP}"
    else:
        # internal deployment
        name = f"{CERTEGO_USERS_PRODUCT_NAME}__{AppChoices.CURRENTAPP}"

    default_product = get_products_prices_map()[name]

    return default_product
