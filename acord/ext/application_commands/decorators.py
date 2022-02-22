from __future__ import annotations
from typing import Any, Callable, Coroutine

from .slash import SlashBase


def autocomplete(*options: str,
    dev_handle: bool = False,
    cls: SlashBase = None,
    on_error: Callable[..., Coroutine[Any, Any, Any]] = None,
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        """Decorator for adding handlers for autocompleting parameters

        Parameters
        ----------
        options: :class:`str`
            Names of option to handle auto completes for,
            use ``*`` to handle any option
        dev_handle: :class:`bool`
            Whether this field will be responded to within the class
        cls: :class:`SlashBase`
            Your command object which this autocomplete should be assigned to,
            this is not needed unless your adding them to commands generated via decorators.
        on_error: Callable[..., Coroutine[Any, Any, Any]]
            A coro which will be called when an error occurs
        """
        def inner(callback: Callable[..., Coroutine[Any, Any, Any]]):
            setattr(
                callback,
                "__autocomplete__",
                (options, dev_handle, on_error)
            )

            if cls is not None:
                setattr(cls, callback.__qualname__, callback)

            return callback

        return inner


def slash_command(**kwargs):
    def inner(callback: Callable[..., Coroutine[Any, Any, Any]]):
        return SlashBase.from_function(callback, **kwargs)

    return inner
