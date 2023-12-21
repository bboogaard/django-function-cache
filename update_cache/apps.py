from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from update_cache.settings import settings


class UpdateCacheConfig(AppConfig):
    name = 'update_cache'
    verbose_name = 'Update cache'

    def ready(self):
        cache_modules = ['cached_functions'] + list(settings.CACHE_MODULES)
        autodiscover_modules(*cache_modules)
