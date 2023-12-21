import datetime
from typing import Any, Callable, Dict, Optional, Protocol, Tuple, Union

from django_rq import enqueue
from django.core.cache import DEFAULT_CACHE_ALIAS
from django.http import HttpRequest
from django.utils.module_loading import import_string
from django.utils.timezone import now

from update_cache.cache.cache import CacheResult, make_cache_key, make_view_cache_key
from update_cache.settings import settings
from update_cache.utils import get_func_name


default_broker = object()


class Broker(Protocol):

    def __call__(self, f: Union[Callable, str], timeout: int,
                 calling_args: Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]] = None,
                 backend: Optional[str] = DEFAULT_CACHE_ALIAS):
        ...


class SyncBroker:

    def __call__(self, f: Union[Callable, str], timeout: int,
                 calling_args: Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]] = None,
                 backend: Optional[str] = DEFAULT_CACHE_ALIAS):
        f = import_string(f) if isinstance(f, str) else f

        try:
            args, kwargs = calling_args
        except ValueError:
            args = ()
            kwargs = {}
        f = getattr(f, '__wrapped__', None) or f
        live_result = f(*args, **kwargs)
        result = CacheResult(
            result=live_result,
            expires=now() + datetime.timedelta(seconds=timeout),
            calling_args=calling_args
        )
        cache_key = make_cache_key(f, calling_args)
        f.cache.set_active(cache_key, result)


sync_broker = SyncBroker()


class AsyncBroker:

    def __call__(self, f: Union[Callable, str], timeout: int,
                 calling_args: Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]] = None,
                 backend: Optional[str] = DEFAULT_CACHE_ALIAS):
        enqueue(sync_broker, get_func_name(f), timeout, calling_args, backend)


async_broker = AsyncBroker()


class ViewBroker(Protocol):

    def __call__(self, f: Union[Callable, str], timeout: int, request: HttpRequest,
                 view_args: Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]] = None,
                 backend: Optional[str] = DEFAULT_CACHE_ALIAS):
        ...


class DefaultViewBroker:

    def __call__(self, f: Union[Callable, str], timeout: int, request: HttpRequest,
                 view_args: Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]] = None,
                 backend: Optional[str] = DEFAULT_CACHE_ALIAS):
        f = import_string(f) if isinstance(f, str) else f

        try:
            args, kwargs = view_args
        except ValueError:
            args = ()
            kwargs = {}
        f = getattr(f, '__wrapped__', None) or f
        live_result = f(request, *args, **kwargs)
        result = CacheResult(
            result=live_result,
            expires=now() + datetime.timedelta(seconds=timeout)
        )
        cache_key = make_view_cache_key(request, request.method)
        f.cache.set_active(cache_key, result)


view_broker = DefaultViewBroker()


def get_broker(broker: Broker = default_broker):
    if broker == default_broker:
        try:
            broker_class = import_string(settings.DEFAULT_BROKER)
            return broker_class()
        except ImportError:
            return sync_broker
    return broker


def get_view_broker(broker: ViewBroker = default_broker):
    if broker == default_broker:
        try:
            broker_class = import_string(settings.DEFAULT_VIEW_BROKER)
            return broker_class()
        except ImportError:
            return view_broker
    return broker
