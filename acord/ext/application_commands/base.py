from __future__ import annotations
from typing import Any, List, Optional

import pydantic
from acord.models import (
    Snowflake,
)
from .types import ApplicationCommandType
from .option import SlashOption


class ApplicationCommand(pydantic.BaseModel):
    application_id: Snowflake
    """ unique id of the parent application """
    id: Snowflake
    """ Unique ID of the command """
    name: str
    """ Name of command """
    description: str
    """ Description of the command, 
    empty strings when type != :attr:`ApplicationCommandType.CHAT_INPUT` """
    version: str
    """autoincrementing version identifier updated during substantial record changes"""
    type: Optional[ApplicationCommandType] = ApplicationCommandType(1)
    """ the type of command, defaults ``1`` if not set """
    guild_id: Optional[Snowflake]
    """ guild id of the command, if not global """
    default_permission: Optional[bool] = True
    """ whether the command is enabled by default when the app is added to a guild """


class SlashExtended(ApplicationCommand):
    options: List[SlashOption]
