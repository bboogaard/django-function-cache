import logging
from functools import wraps

from django.core.cache import caches, DEFAULT_CACHE_ALIAS
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from update_cache.brokers import Broker, default_broker, ViewBroker
from update_cache.cache.cache import make_cache_key, make_view_cache_key
from update_cache.cache.registry import function_cache_registry
from update_cache.cache.update import DefaultUpdateHandler, ViewUpdateHandler


logger = logging.getLogger(__name__)


def cache_function(timeout: int = DEFAULT_TIMEOUT, backend: str = DEFAULT_CACHE_ALIAS, broker: Broker = default_broker):

    cache = caches[backend]

    def decorator(f):

        f.cache = function_cache_registry.add(f, cache)
        update_handler = DefaultUpdateHandler(f.cache, timeout, backend, broker)

        @wraps(f)
        def wrapped_func(*args, **kwargs):
            cache_key = make_cache_key(f, (args, kwargs))
            return update_handler.get_result(cache_key, *args, **kwargs)

        return wrapped_func

    return decorator


def cache_view(timeout: int = DEFAULT_TIMEOUT, backend: str = DEFAULT_CACHE_ALIAS, broker: ViewBroker = default_broker):

    cache = caches[backend]

    def decorator(view):

        view.cache = function_cache_registry.add(view, cache)
        update_handler = ViewUpdateHandler(view.cache, timeout, backend, broker)

        @wraps(view)
        def wrapped_view(request, *args, **kwargs):
            cache_key = make_view_cache_key(request, request.method)
            return update_handler.get_result(cache_key, request, *args, **kwargs)

        return wrapped_view

    return decorator
