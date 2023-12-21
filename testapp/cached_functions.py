import random
from string import ascii_uppercase

from django.utils.crypto import get_random_string
from update_cache.brokers import async_broker
from update_cache.decorators import cache_function


@cache_function()
def create_random_strings(num: int):
    result = []
    for i in range(num):
        result.append(get_random_string(100))
    return result


@cache_function(timeout=60)
def create_random_numbers(num: int):
    result = []
    for i in range(num):
        result.append(str(random.randint(1, 100)))
    return result


@cache_function(broker=async_broker)
def create_random_letters(num: int):
    letters = ascii_uppercase
    result = []
    for i in range(num):
        result.append(random.choice(letters))
    return result


@cache_function(backend='dummy')
def create_random_words(num: int):
    words = ('Foo', 'Bar', 'Baz')
    result = []
    for i in range(num):
        result.append(random.choice(words))
    return result
