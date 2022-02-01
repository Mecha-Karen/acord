from __future__ import annotations
from typing import Any, List, Optional
import pydantic

from .types import ApplicationCommandOptionType
from acord.bases import ChannelTypes
from acord.errors import SlashOptionError


class GenericApplicationOption(pydantic.BaseModel):
    type: ApplicationCommandOptionType
    """ Type of option """
    name: str
    """ Name of option """
    description: str
    """ Description of option """
    choices: Optional[List[Any]]
    """ List of choices user can choose from """
    required: Optional[bool] = False
    """ Whether this option is required """
    options: Optional[List[GenericApplicationOption]]
    """ If this a sub-group, what other options are there """
    channel_types: Optional[List[ChannelTypes]]
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
            if any(i for i in self.options if i.type == ApplicationCommandOptionType.SUB_COMMAND_GROUP):
                raise SlashOptionError("Slash option group may not contain another group")
        if len(self.choices) > 25:
            raise SlashOptionError("Slash option cannot contain more then 25 choices")
        if self.choices and self.autocomplete:
            raise SlashOptionError("autocomplete set to ``True`` when choices provided")
