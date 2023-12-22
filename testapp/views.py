from django.http.response import HttpResponse, StreamingHttpResponse
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from update_cache.decorators import cache_view

from testapp import cached_functions
from testapp import utils


def strings(request):
    content = cached_functions.create_random_strings(100)
    return HttpResponse('\n'.join(content), content_type='text/plain')


def numbers(request):
    content = cached_functions.create_random_numbers(100)
    return HttpResponse('\n'.join(content), content_type='text/plain')


def letters(request):
    content = cached_functions.create_random_letters(100)
    return HttpResponse('\n'.join(content), content_type='text/plain')


def words(request):
    content = cached_functions.create_random_words(100)
    return HttpResponse('\n'.join(content), content_type='text/plain')


@cache_view()
def short_strings(request):
    content = utils.create_random_strings(100)
    return HttpResponse('\n'.join(content), content_type='text/plain')


@cache_view(timeout=60)
def low_numbers(request):
    content = utils.create_random_numbers(100)
    return TemplateResponse(request, 'numbers.txt', context={'content': '\n'.join(content)}, content_type='text/plain')


class LowerCaseLetters(APIView):

    renderer_classes = [renderers.JSONRenderer]

    @method_decorator(cache_view(backend='dummy'))
    def get(self, request, *args, **kwargs):
        content = utils.create_random_letters(100)
        return Response('\n'.join(content))


@cache_view()
def lorem_words(request):
    def _stream():
        for word in utils.create_random_words(100):
            yield word

    return StreamingHttpResponse(_stream())


@cache_view()
def error(request):
    content = utils.create_random_strings(100)
    return HttpResponse('\n'.join(content), content_type='text/plain', status=400)


@cache_view()
def with_cookie(request):
    content = utils.create_random_strings(100)
    response = HttpResponse('\n'.join(content), content_type='text/plain')
    response.headers['Vary'] = 'Cookie'
    response.cookies['csrftoken'] = 'asdf'
    return response


@cache_view()
def private_cache(request):
    content = utils.create_random_strings(100)
    response = HttpResponse('\n'.join(content), content_type='text/plain')
    response.headers['Cache-Control'] = 'private'
    return response
