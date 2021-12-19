from __future__ import annotations
from typing import List, Optional

from acord.bases import PermissionsOverwrite
from acord.models import Snowflake

from .base import Channel


class VoiceChannel(Channel):
    guild_id: Snowflake
    """ ID of guild were channel is in """
    name: str
    """ Name of channel """
    nsfw: bool
    """ Whether the channel is marked as NSFW """
    position: int
    """ Position of channel """
    permissions_overwrite: List[PermissionsOverwrite]
    """ Permissions for channel """
    bitrate: int
    """ the bitrate (in bits) of the voice channel """
    user_limit: int
    """ the user limit of the voice channel """
    parent_id: Optional[Snowflake]
    """ ID of category were channel is in """
    rtc_region: Optional[str]
    """ voice region id for the voice channel, automatic when set to null """
