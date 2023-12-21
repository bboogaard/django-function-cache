from typing import Callable, List

from django.core.cache.backends.base import BaseCache
from django.utils.timezone import now

from update_cache.cache.cache import ACTIVE_VERSION, CACHE_KEY_PREFIX, CacheResult, EXPIRED_VERSION, missing
from update_cache.utils import get_func_name


class CachedFunction:

    f: Callable

    func_name: str

    cache: BaseCache

    def __init__(self, f: Callable, cache: BaseCache):
        self.f = f
        self.func_name = get_func_name(f)
        self.cache = cache

    def get_active(self, key, default=missing) -> CacheResult:
        return self.cache.get(key, default, version=ACTIVE_VERSION)

    def set_active(self, key, value: CacheResult):
        self.cache.set(key, value, timeout=None, version=ACTIVE_VERSION)
        self._add_entry(key)
        self.cache.delete(key, version=EXPIRED_VERSION)

    def get_expired(self, key, default=missing) -> CacheResult:
        return self.cache.get(key, default, version=EXPIRED_VERSION)

    def set_expired(self, key, value: CacheResult):
        value.expires = now()
        self.cache.set(key, value, timeout=None, version=EXPIRED_VERSION)
        self.cache.delete(key, version=ACTIVE_VERSION)

    def invalidate(self, key):
        value = self.get_active(key, missing)
        if value != missing:
            self.set_expired(key, value)

    def delete(self, key):
        self.cache.delete(key, version=ACTIVE_VERSION)
        self.cache.delete(key, version=EXPIRED_VERSION)
        self._delete_entry(key)

    def __iter__(self):
        return iter(self._get_entries())

    def _add_entry(self, key):
        self.cache.set(self._make_key(), self._get_entries() | {key}, timeout=None)

    def _delete_entry(self, key):
        self.cache.set(self._make_key(), self._get_entries() - {key})

    def _get_entries(self):
        return self.cache.get(self._make_key()) or set()

    def _make_key(self):
        return ':'.join([CACHE_KEY_PREFIX, self.func_name])


class FunctionCacheRegistry:

    cached_functions: List[CachedFunction]

    def __init__(self):
        self.cached_functions = []

    def add(self, f: Callable, cache: BaseCache) -> CachedFunction:
        cached_function = CachedFunction(f, cache)
        self.cached_functions.append(cached_function)
        return cached_function

    def __iter__(self):
        return iter(self.cached_functions)


function_cache_registry = FunctionCacheRegistry()
