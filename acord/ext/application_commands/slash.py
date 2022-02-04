from __future__ import annotations
import inspect
from subprocess import call
import pydantic
from typing import List, Optional

from .option import SlashOption
from .types import ApplicationCommandType
from .base import UDAppCommand
from .model_based import EXTENDED_CALLS

from acord.errors import SlashCommandError
from acord.bases import _C


VALID_ATTR_NAMES = (
    "name",
    "description",
    "options",
    "default_permission",
    "guild_ids",
    "extend",
    "overwrite",
)


class SlashBase(UDAppCommand):
    """Base class for creating slash commands.

    .. rubric:: Guidance

    When creating slash commands you have 2 options,
    intialise this class normally (ex1).
    Or subclass it and add your attrs through:
    * class variables
    * direct call to super().__init__

    .. note::
        All args can be passed through the init subclass apart from,
        ``overwrite`` and ``extend``,
        read below for further guidance.

    .. note::
        * Max 25 options
        * Entire slash commands values must be less then 4k characters,
          (Dont panic this is handled for you!)
        * Name must be under 32 characters
        * Description must be under 100 characters

    For a more clearer example make sure to check out the examples in the github repo.

    .. rubric:: Valid on_call names

    on_call's can be registered directly from creating the class or :meth:`SlashBase.set_call`.

    Below they are represented as a list,
    were each element is the function signiture

    callback: [:class:`Interaction`, **options]
        Called when command is used,
        must be provided
    on_error: [:class:`Interaction`, exc_info]
        Called when an error occurs during handling of command.

    Parameters
    ----------
    All values from attributes are considered arguments,
    and will be used to create the model.

    extend: :class:`bool`
        Whether to extend attributes if they were provided twice,
        doesn't check if they are the same! Defaults to ``True``.
    overwrite: :class:`bool`
        Whether to overwrite this command if it already exists,
        defaults to ``False``.

    When using args whilst subclassing,
    ``extend`` becomes ``extendable``
    and ``overwrite`` becomes ``overwritable``.
    """

    name: str
    """ name of command """
    description: str
    """ description of the command """
    options: Optional[List[SlashOption]] = []
    """ array of options (your parameters) """
    default_permission: Optional[bool] = True
    """ whether the command is enabled by default when the app is added to a guild """
    guild_ids: Optional[List[int]] = None
    """ list of guilds to restrict command to """

    overwrite: bool = False
    extend: bool = True
    __pre_calls__: dict = {}

    def dict(self, **kwds) -> dict:
        """:meta private:"""
        d = super(SlashBase, self).dict(**kwds)

        to_pop = ["guild_ids", "overwrite", "extend", "__pre_calls__"]
        to_pop.extend(getattr(self, "__ignore__", []))

        for key in to_pop:
            d.pop(key, None)

        d["type"] = ApplicationCommandType.CHAT_INPUT

        return d

    def __new__(cls, *args, **kwds):
        # Generates new slash command on call
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

        return super(SlashBase, cls).__new__(cls)

    def __init__(self, **kwds) -> None:
        __pre_calls__ = {**self.__pre_calls__, **kwds.pop("calls", {})}
        for call_identifier in EXTENDED_CALLS:
            if call_identifier in kwds:
                __pre_calls__[call_identifier] = kwds[call_identifier]

        if "callback" not in __pre_calls__:
            raise SlashCommandError("Slash command missing callback")

        super().__init__(**kwds)

        if not all(i for i in self.options if type(i) == SlashOption):
            raise SlashCommandError(
                "Options in a slash command must all be of type SlashOption"
            )

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

            field = SlashBase.__fields__[attr]
            field.validate(n_attr, {}, loc=field.alias)

        setattr(cls, "__pre_calls__", {})
        for attr in EXTENDED_CALLS:
            if hasattr(cls, attr):
                cls.__pre_calls__[attr] = getattr(cls, attr)

        return cls

    def _total_chars(self):
        total = 0
        total += len(self.name) + len(self.description)

        for attr in self.__annotations__:
            attr_value = getattr(self, attr)

            if hasattr(attr_value, "_total_chars"):
                total += attr_value._total_chars()
            else:
                total += len(attr_value)

        return total

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

    def add_option(self, option: SlashOption) -> None:
        """Adds a specified option to the command,
        this method is preferred to be called as it handles slash command limits!

        Parameters
        ----------
        option: :class:`SlashOption`
            new option to be added to slash command
        """
        if (self._total_chars() + option._total_chars()) > 4000:
            raise SlashCommandError("Slash command exceeded 4k characters")
        if (len(self.options) + 1) > 25:
            raise SlashCommandError("Slash command must have less then 25 options")

        self.options.append(option)

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
                        self, interaction, (type(exc), exc, exc.__traceback__)
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

    @property
    def type(self):
        """Returns the type of command, always ``1``"""
        return ApplicationCommandType.CHAT_INPUT
