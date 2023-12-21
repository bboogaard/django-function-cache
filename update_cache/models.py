import operator

from django.db import models
from django.db.models.query import BaseIterable

from update_cache.cache.cache import missing
from update_cache.cache.registry import function_cache_registry


class CacheEntryIterable(BaseIterable):

    def __iter__(self):
        for cached_function in list(sorted(function_cache_registry, key=operator.attrgetter('func_name'))):
            for key in list(sorted(cached_function)):
                active_value = cached_function.get_active(key, missing)
                expired_value = cached_function.get_expired(key, missing)
                if active_value != missing:
                    value = str(active_value.result)
                    calling_args = str(active_value.calling_args)
                    expires = active_value.expires
                    has_expired = active_value.has_expired
                elif expired_value != missing:
                    value = str(expired_value.result)
                    calling_args = str(expired_value.calling_args)
                    expires = expired_value.expires
                    has_expired = True
                else:
                    value = ''
                    calling_args = ''
                    expires = None
                    has_expired = False
                cache_entry = CacheEntry(
                    cache_key=key,
                    function=cached_function.func_name,
                    calling_args=calling_args,
                    value=value,
                    expires=expires,
                    has_expired=has_expired
                )
                cache_entry._cached_function = cached_function
                yield cache_entry


class CacheEntryQuerySet(models.QuerySet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._iterable_class = CacheEntryIterable

    def count(self):
        if self._result_cache is not None:
            return len(self._result_cache)

        return len(list(self._iterable_class(self)))


class CacheEntry(models.Model):

    cache_key = models.CharField(max_length=255, primary_key=True)

    function = models.CharField(max_length=255)

    calling_args = models.TextField(blank=True)

    value = models.TextField()

    expires = models.DateTimeField(null=True)

    has_expired = models.BooleanField(default=False)

    objects = CacheEntryQuerySet.as_manager()

    class Meta:
        managed = False
        verbose_name = 'Cache entry'
        verbose_name_plural = 'Cache entries'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_function = None

    def __str__(self):
        return self.cache_key

    @property
    def cached_function(self):
        return self._cached_function
