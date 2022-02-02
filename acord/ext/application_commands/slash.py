from __future__ import annotations
from typing import List, Optional

from .option import SlashOption
from .types import ApplicationCommandType
from .base import UDAppCommand
from acord.errors import SlashCommandError
from acord.bases import _C


VALID_ATTR_NAMES = (
    "name", "description",
    "callback", "options",
    "default_permission",
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
        * Max 25 options
        * Entire slash commands values must be less then 4k characters,
          (Dont panic this is handled for you!)
        * Name must be under 32 characters
        * Description must be under 100 characters

    For a more clearer example make sure to check out the examples in the github repo.

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
    callback: _C = None
    """ Callback for when the command is used """
    on_error: Optional[_C] = None
    """ Callback for when an error occurs during handling of command """
    options: Optional[List[SlashOption]] = []
    """ array of options (your parameters) """
    default_permission: Optional[bool] = True
    """ whether the command is enabled by default when the app is added to a guild """
    guild_ids: Optional[List[int]] = None
    """ list of guilds to  """

    def dict(self, **kwds) -> dict:
        """ :meta private: """
        d = super(SlashBase, self).dict(**kwds)

        d.pop("callback")
        d.pop("guild_ids")
        d.pop("on_error")
        d["type"] = ApplicationCommandType.CHAT_INPUT

        return d

    def __new__(cls, **kwds):
        # Generates new slash command on call
        # Adds pre-existing args from cls to kwds and calls init
        # returning generated slash command
        extend = kwds.get("extend", False) or hasattr(cls, "__extend_if_provided")

        for attr in VALID_ATTR_NAMES:
            a_ = getattr(cls, attr, None)

            if attr in kwds and extend:
                if hasattr(a_, "extend"):
                    a_.extend(kwds[attr])

            if not a_:
                continue

            kwds.update({attr: a_})

        return super(SlashBase, cls).__new__(cls, **kwds)

    def __init__(self, **kwds) -> None:
        if not getattr(self, "_extend_if_provided"):
            self._extend_if_provided = kwds.pop("extend", True)
        if not getattr(self, "_overwrite_if_exists"):
            self._overwrite_if_exists = kwds.pop("overwrite", False)

        super().__init__(**kwds)

        if not all(i for i in self.options if type(i) == SlashOption):
            raise SlashCommandError("Options in a slash command must all be of type SlashOption")

    def __init_subclass__(cls, **kwds) -> None:
        # kwds is validated in the second for loop
        extend = kwds.pop("extendable", True)
        overwrite = kwds.pop("overwritable", False)
        cls._extend_if_provided = extend
        cls._overwrite_if_exists = overwrite

        for attr in kwds:
            if attr in VALID_ATTR_NAMES:
                setattr(cls, attr, kwds[attr])

        for attr in VALID_ATTR_NAMES:
            n_attr = getattr(cls, attr, None)

            field = SlashBase.__fields__[attr]
            field.validate(n_attr, {}, loc=field.alias)

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

    async def dispatcher(self, interaction, **kwds) -> int:
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
        try:
            await self.callback(interaction, **kwds)
        except Exception as exc:
            if self.callback and self.on_error:
                try:
                    await self.on_error(
                        interaction,
                        (type(exc), exc, exc.__traceback__)
                    )
                except Exception as e_exc:
                    return e_exc
        else:
            return 0
        return 1

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
        kwds.update(callback=function)

        return cls(**kwds)

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
