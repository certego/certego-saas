from cache_memoize import cache_memoize as _cache_memoize
from django.core.cache import caches

from .consts import CACHE_ALIAS

__all__ = ["cache_memoize", "get_cache"]


def cache_memoize(*args, **kwargs):
    return _cache_memoize(*args, **kwargs, cache_alias=CACHE_ALIAS)


def get_cache():
    """
    tries to get the ``api.payments`` cache
    otherwise fallback to ``default`` cache
    """
    try:
        return caches[CACHE_ALIAS]
    except KeyError:
        return caches["default"]
