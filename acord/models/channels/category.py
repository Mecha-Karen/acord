from __future__ import annotations
from typing import List

from acord.bases import PermissionsOverwrite
from acord.models import Snowflake

from .base import Channel


class CategoryChannel(Channel):
    permission_overwrites: List[PermissionsOverwrite]
    """ List of permissions for category """
    name: str
    """ Name of category """
    nsfw: bool
    """ Whether the category is marked as NSFW """
    position: int
    """ Position of category """
    guild_id: Snowflake
    """ ID of guild were category belongs """
