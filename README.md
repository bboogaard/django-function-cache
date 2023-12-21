# django-update-cache

Lazy cache updates for Django.

## Rationale

Cache function results with optional asynchronous updates.

## Support

Supports: Python 3.10.

Supports Django Versions: 4.2.7

## Installation

```shell
$ pip install django-update-cache
```

## Usage

Add `update_cache.apps.UpdateCacheConfig` to `INSTALLED_APPS`.

Run migrations:

```shell
python manage.py migrate
```

Add a module `cached_functions` to one or more of your apps. Decorate any function for which you want the results to be 
cached:

```python
# cached_functions.py
from update_cache.decorators import cache_function


@cache_function()
def my_expensive_function():
    ...
```

Specify a specific timeout:

```python
# cached_functions.py
from update_cache.decorators import cache_function


@cache_function(timeout=60)
def my_expensive_function():
    ...
```

Use asynchronous updating (this requires running a django_rq worker):

```python
# cached_functions.py
from update_cache.brokers import async_broker
from update_cache.decorators import cache_function


@cache_function(broker=async_broker)
def my_expensive_function():
    ...
```

Use a custom cache backend:

```python
# cached_functions.py
from update_cache.decorators import cache_function


@cache_function(backend='my_cache_alias')
def my_expensive_function():
    ...
```

You can set a global broker to delegate the cache updates in `settings.py`.

```python
DUC_DEFAULT_BROKER = 'update_cache.brokers.AsyncBroker'
```

Invalidate the cache:

```python
# cached_functions.py
from update_cache.decorators import cache_function


@cache_function()
def my_expensive_function():
    ...


my_expensive_function.cache.invalidate()
```

Cache a view (only synchronous updates).

```python
# cached_functions.py
from update_cache.decorators import cache_view


@cache_view()
def my_expensive_view():
    ...
```

View all cached entries in Django Admin:

![cached entries](./cache-entries.png "Cached entries")
