from django.http import HttpRequest
from django.http.response import HttpResponse
from django.utils.cache import has_vary_header


def should_cache_view(request: HttpRequest, response: HttpResponse):
    if request.method != 'GET':
        return False

    if response.streaming or response.status_code not in (200, 304):
        return False

    # Don't cache responses that set a user-specific (and maybe security
    # sensitive) cookie in response to a cookie-less request.
    if (
            not request.COOKIES
            and response.cookies
            and has_vary_header(response, "Cookie")
    ):
        return False

    # Don't cache a response with 'Cache-Control: private'
    if "private" in response.get("Cache-Control", ()):
        return False

    return True
