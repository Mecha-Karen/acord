from __future__ import annotations
from typing import Any, List, Optional, Union
import pydantic

from .types import ApplicationCommandOptionType
from acord.bases import ChannelTypes
from acord.errors import SlashOptionError


class ApplicationChoice(pydantic.BaseModel):
    name: str
    value: Any

    def _total_chars(self):
        return len(self.name) + len(str(self.value))


class GenericApplicationOption(pydantic.BaseModel):
    type: ApplicationCommandOptionType
    """ Type of option """
    name: str
    """ Name of option """
    description: str
    """ Description of option """
    choices: Optional[List[ApplicationChoice]] = []
    """ List of choices user can choose from """
    required: Optional[bool] = False
    """ Whether this option is required """
    options: Optional[List[GenericApplicationOption]] = []
    """ If this a sub-group, what other options are there """
    channel_types: Optional[List[ChannelTypes]] = []
    """ If type is :attr:`ApplicationCommandOptionType.CHANNEL`, 
    what types should be allowed """
    min_value: Optional[int]
    """ If type is 
    :attr:`ApplicationCommandOptionType.NUMBER`/:attr:`ApplicationCommandOptionType.INTEGER`, 
    what is the minimum value """
    max_value: Optional[int]
    """ If type is 
    :attr:`ApplicationCommandOptionType.NUMBER`/:attr:`ApplicationCommandOptionType.INTEGER`, 
    what is the maximum value """
    autocomplete: Optional[bool]
    """ Whether to autocomplete user,
    must stay as False when choices are provided
    """

    def _total_chars(self):
        total = 0

        for attr in self.__annotations__:
            attr_value = getattr(self, attr)

            if hasattr(attr_value, "_total_chars"):
                total += attr_value._total_chars()
            else:
                total += len(str(attr_value))

        return total


class SlashOption(GenericApplicationOption):
    """Used for validating options in slash commands.
    This class should be used instead of GenericApplicationOption.

    **Rules:**
    * A SlashOption which is acting as a group may not have another group within it
    * autocomplete must be ``False`` when choices is provided
    * Must be less then 25 choices
    """

    def __init__(self, **kwds) -> None:
        super().__init__(**kwds)

        if self.type == ApplicationCommandOptionType.SUB_COMMAND_GROUP:
            if any(
                i
                for i in self.options
                if i.type == ApplicationCommandOptionType.SUB_COMMAND_GROUP
            ):
                raise SlashOptionError(
                    "Slash option group may not contain another group"
                )
        else:
            if self.options:
                raise SlashOptionError("Only sub command groups may have options")

        if len(self.choices) > 25:
            raise SlashOptionError("Slash option cannot contain more then 25 choices")
        if self.choices and self.autocomplete:
            raise SlashOptionError("autocomplete set to ``True`` when choices provided")

    def is_group(self):
        return self.type == ApplicationCommandOptionType.SUB_COMMAND_GROUP


class AutoCompleteChoice(pydantic.BaseModel):
    name: str
    value: Union[str, int, float]
