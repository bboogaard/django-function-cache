import random
from string import ascii_lowercase

from django.utils.crypto import get_random_string


def create_random_strings(num: int):
    result = []
    for i in range(num):
        result.append(get_random_string(10))
    return result


def create_random_numbers(num: int):
    result = []
    for i in range(num):
        result.append(str(random.randint(1, 10)))
    return result


def create_random_letters(num: int):
    letters = ascii_lowercase
    result = []
    for i in range(num):
        result.append(random.choice(letters))
    return result
