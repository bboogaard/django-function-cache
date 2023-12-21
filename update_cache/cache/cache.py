import datetime
import hashlib
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

from django.conf import settings
from django.http import HttpRequest
from django.utils.timezone import get_current_timezone_name, now
from django.utils.translation import get_language

from update_cache.utils import get_func_name


CACHE_KEY_PREFIX = 'duc'

ACTIVE_VERSION = 1
EXPIRED_VERSION = 2


missing = object()


@dataclass
class CacheResult:
    result: Any
    expires: datetime.datetime
    calling_args: Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]] = None

    @property
    def has_expired(self) -> bool:
        return now() >= self.expires


def make_cache_key(f: Callable, calling_args: Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]] = None) -> str:
    func_name = get_func_name(f)
    arg_part = hashlib.md5(str(calling_args).encode(), usedforsecurity=False).hexdigest()
    return ':'.join([CACHE_KEY_PREFIX, func_name, arg_part])


def make_view_cache_key(request: HttpRequest, method: str) -> str:
    url = hashlib.md5(request.build_absolute_uri().encode("ascii"), usedforsecurity=False)
    language_part = getattr(request, "LANGUAGE_CODE", get_language()) if settings.USE_I18N else None
    timezone_part = get_current_timezone_name() if settings.USE_TZ else None
    return ':'.join(filter(None, [CACHE_KEY_PREFIX, method, url.hexdigest(), language_part, timezone_part]))
