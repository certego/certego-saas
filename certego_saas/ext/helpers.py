import re
from typing import Tuple

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.exceptions import ValidationError as DRFValidationError


def parse_humanized_range(range_str: str) -> Tuple[timezone.datetime, str]:
    """
    Utility function to parse time range given as a ``str``.
    Used in metrics/aggregation views.
    """
    unit_duration_map = {"h": 3600, "d": 86400, "M": 2592000, "Y": 31536000}
    unit_basis_map = {"h": "hour", "d": "day", "M": "month", "Y": "year"}
    pattern = r"(\d+)(h|d|M|Y)"

    result = re.match(pattern, range_str)
    if result:
        value, unit = result.groups()
        delta = timezone.now() - timezone.timedelta(
            seconds=int(value) * unit_duration_map[unit]
        )
        basis = unit_basis_map[unit]
        return delta, basis
    raise DRFValidationError(f"Invalid range. Pattern should be: '{pattern}'.")


def cache_action_response(*args, **kwargs):
    """
    Decorator to apply cache to a DRF's ``@action`` view.
    """
    return method_decorator(cache_page(*args, **kwargs))
