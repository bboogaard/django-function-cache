import inspect
from typing import Callable


def get_func_name(f: Callable) -> str:
    return '{}.{}'.format(inspect.getmodule(f).__name__, f.__name__)
