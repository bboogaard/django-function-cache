from typing import List

from django.conf import settings as django_settings


default_settings = {
    "DEFAULT_BROKER": 'update_cache.brokers.SyncBroker',
    "DEFAULT_VIEW_BROKER": 'update_cache.brokers.SyncViewBroker',
    "CACHE_MODULES": []
}


class Settings:

    DEFAULT_BROKER: str

    DEFAULT_VIEW_BROKER: str

    CACHE_MODULES: List[str]

    def __getattr__(self, item):
        return getattr(django_settings, 'DUC_' + item, default_settings.get(item))


settings = Settings()
