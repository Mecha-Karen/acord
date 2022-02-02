from __future__ import annotations
from typing import Any, Callable, Coroutine

import inspect
from .slash import SlashBase


def slash_command(**kwargs):
    def inner(callback: Callable[..., Coroutine[Any, Any, Any]]):
        return SlashBase.from_function(callback, **kwargs)
    return inner
