from __future__ import annotations
from re import A
from typing import Any, List, Optional
import pydantic

from .option import SlashOption
from .types import ApplicationCommandType
from acord.errors import SlashCommandError
from acord.bases import _C


VALID_ATTR_NAMES = (
    "name", "description",
    "callback", "options",
    "default_permission",
)


class SlashBase(pydantic.BaseModel):
    name: str
    """ name of command """
    description: str
    """ description of the command """
    callback: Optional[_C] = None
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
        super().__init__(**kwds)

        if not all(i for i in self.options if type(i) == SlashOption):
            raise SlashCommandError("Options in a slash command must all be of type SlashOption")

    def __init_subclass__(cls, **kwds) -> None:
        # kwds is validated in the second for loop
        extend = kwds.pop("extend", False)
        cls._extend_if_provided = extend

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
        # 0 => Dispatched without error
        # 1 => Dispatched but an error occured
        # Exception => Dispatched but an error occured with both callback and error handler
        try:
            await self.callback(interaction, **kwds)
        except Exception as exc:
            if self.callback and self.on_error:
                try:
                    await self.on_error(exc)
                except Exception as e_exc:
                    return e_exc
        else:
            return 0
        return 1

    @classmethod
    def from_function(cls, function: _C, **kwds) -> None:
        kwds.update(callback=function)

        return cls(**kwds)

    def add_option(self, option: SlashOption) -> None:
        if (self._total_chars() + option._total_chars()) > 4000:
            raise SlashCommandError("Slash command exceeded 4k characters")

        self.options.append(option)
