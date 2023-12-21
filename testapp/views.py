from django.http.response import HttpResponse
from update_cache.decorators import cache_view

from testapp import cached_functions
from testapp import utils


def strings(request):
    content = list(cached_functions.create_random_strings(100))
    return HttpResponse('\n'.join(content), content_type='text/plain')


def numbers(request):
    content = list(cached_functions.create_random_numbers(100))
    return HttpResponse('\n'.join(content), content_type='text/plain')


def letters(request):
    content = list(cached_functions.create_random_letters(100))
    return HttpResponse('\n'.join(content), content_type='text/plain')


def words(request):
    content = list(cached_functions.create_random_words(100))
    return HttpResponse('\n'.join(content), content_type='text/plain')


@cache_view()
def short_strings(request):
    content = list(utils.create_random_strings(100))
    return HttpResponse('\n'.join(content), content_type='text/plain')


@cache_view(timeout=60)
def low_numbers(request):
    content = list(utils.create_random_numbers(100))
    return HttpResponse('\n'.join(content), content_type='text/plain')


@cache_view(backend='dummy')
def lowercase_letters(request):
    content = list(utils.create_random_letters(100))
    return HttpResponse('\n'.join(content), content_type='text/plain')
