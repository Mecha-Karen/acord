# m_based simply stands for model based
# meaning command that are dependant on a model such as a message
from __future__ import annotations
from email.mime import application

from typing import List, Optional
import inspect

from .base import UDAppCommand
from .types import ApplicationCommandType
from acord.errors import ApplicationCommandError
from acord.bases import _C


VALID_ATTR_NAMES = (
    "name",
    "default_permission",
    "guild_ids", "overwrite",
    "extend"
)

EXTENDED_CALLS = (
    "callback",
    "on_error"
)


class GenericModelCommand(UDAppCommand):
    name: str
    """ name of command """
    type: ApplicationCommandType
    """ Type of command """
    default_permission: Optional[bool] = True
    """ whether the command is enabled by default when the app is added to a guild """
    guild_ids: Optional[List[int]] = None
    """ list of guilds to restrict command to """

    overwrite: bool = False
    extend: bool = True
    __pre_calls__: dict = {}

    def __new__(cls, **kwds):
        # Generates new command on call
        # Adds pre-existing args from cls to kwds and calls init
        # returning generated slash command
        extend = kwds.get("extend", False) or getattr(cls, "extend", False)

        for attr in VALID_ATTR_NAMES:
            a_ = getattr(cls, attr, None)

            if attr in kwds and extend:
                if hasattr(a_, "extend"):
                    a_.extend(kwds[attr])

            if not a_:
                continue

            kwds.update({attr: a_})

        return super(GenericModelCommand, cls).__new__(cls)

    def __init__(self, **kwds) -> None:
        __pre_calls__ = {**self.__pre_calls__, **kwds.pop("calls", {})}
        for call_identifier in EXTENDED_CALLS:
            if call_identifier in kwds:
                __pre_calls__[call_identifier] = kwds[call_identifier]

        if "callback" not in __pre_calls__:
            raise ApplicationCommandError("Command missing callback")

        super().__init__(**kwds)

    def __init_subclass__(cls, **kwds) -> None:
        # kwds is validated in the second for loop
        extend = kwds.pop("extendable", True)
        overwrite = kwds.pop("overwritable", False)
        cls.extend = extend
        cls.overwrite = overwrite

        for attr in kwds:
            if attr in VALID_ATTR_NAMES:
                setattr(cls, attr, kwds[attr])

        for attr in VALID_ATTR_NAMES:
            n_attr = getattr(cls, attr, None)

            field = cls.__fields__[attr]
            field.validate(n_attr, {}, loc=field.alias)

        setattr(cls, "__pre_calls__", {})
        for attr in EXTENDED_CALLS:
            if hasattr(cls, attr):
                cls.__pre_calls__[attr] = getattr(cls, attr)

        return cls

    def dict(self, **kwds) -> dict:
        """ :meta private: """
        d = super(GenericModelCommand, self).dict(**kwds)

        d.pop("guild_ids")
        d.pop("overwrite")
        d.pop("extend")
        d.pop("__pre_calls__", None)

        return d

    def set_call(self, name: str, function: _C) -> None:
        f"""|coro|

        Registers a function to be called on a certain condition,
        class must have "callback" registered and is done when intiating the class.

        Parameters
        ----------
        name: :class:`str`
            Name of call, any from:

            {", ".join(EXTENDED_CALLS)}
        function: Callable[..., Coroutine]
            A coroutine function to be called on dispatch
        """
        if not inspect.iscoroutinefunction(function):
            raise TypeError("Function must be a coroutine function")
        self.__pre_calls__.update({name: function})

    async def dispatcher(self, interaction, future, **kwds) -> int:
        """|coro|

        Default dispatch handler for when the slash command is used,
        handles callback and on_error calls.

        .. rubric:: Return Codes

        0:
            Dispatched without error
        1:
            Dispatched but an error occured,
            on_error was called if accessible
        Exception of any type:
            Dispatched but an error occured with both callback and error handler
        """
        # 0 => Dispatched without error
        # 1 => Dispatched but an error occured
        # Exception => Dispatched but an error occured with both callback and error handler
        callback = self.__pre_calls__.get("callback")
        on_error = self.__pre_calls__.get("on_error")

        # Weird behaviour during testing, but oh well
        try:
            await callback(self, interaction, **kwds)
        except Exception as exc:
            if on_error:
                try:
                    await on_error(
                        self,
                        interaction,
                        (type(exc), exc, exc.__traceback__)
                    )
                except Exception as e_exc:
                    return future.set_result(e_exc)
            else:
                future.set_result(exc)
        else:
            return future.set_result(0)
        return future.set_result(1)

    @classmethod
    def from_function(cls, function: _C, **kwds) -> None:
        """Generates slash command from a function, 
        taking same kwargs and options as intiating the command normally.

        Parameters
        ----------
        function: Callable[..., Coroutine]
            An async function which acts like the callback
        **kwds:
            Additional kwargs such as "name", "description".
        """
        sc_ff = cls(**kwds)
        sc_ff.set_callback(function)
        return sc_ff


# NOTE: The actual commands

class UserCommand(GenericModelCommand):
    """User commands are commands that can be ran by right clicking a user

    They follow the same structure as slash commands and parameters,
    which can be found here at :class:`SlashCommands`.

    .. rubric:: Callback Function

    Callback function with user have the following signiture:

    [:class:`Interaction`, :class:`User`]

    .. note::
        User may be the ID if cannot be fetched from cache
    """
    def __init__(self, **kwds) -> None:
        kwds.update({"type": ApplicationCommandType.USER})

        super().__init__(**kwds)


class MessageCommand(GenericModelCommand):
    """User commands are commands that can be ran by right clicking a message

    They follow the same structure as slash commands and parameters,
    which can be found here at :class:`SlashCommands`.

    .. rubric:: Callback Function

    Callback function with message have the following signiture:

    [:class:`Interaction`, :class:`Message`]

    .. note::
        Message may be the ID if cannot be fetched from cache
    """
    def __init__(self, **kwds) -> None:
        kwds.update({"type": ApplicationCommandType.MESSAGE})

        super().__init__(**kwds)
