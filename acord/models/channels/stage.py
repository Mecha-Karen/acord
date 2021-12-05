from __future__ import annotations
import pydantic

from .__main__ import Channel

from acord.models import Snowflake
from acord.bases import Hashable
from typing import Any, Literal


class Stage(Channel, Hashable):
    guild_id: Snowflake
    # The guild id of the associated Stage channel
    channel_id: Snowflake
    # The id of the associated Stage channel
    topic: str
    # The topic of the Stage instance (1-120 characters)
    privacy_level: Literal[1, 2]
    # The privacy level of the Stage instance
    discoverable_disabled: bool
    # Whether or not Stage Discovery is disabled
