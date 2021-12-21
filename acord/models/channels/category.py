from __future__ import annotations
from typing import List, Optional

from acord.bases import PermissionsOverwrite
from acord.models import Snowflake

from .base import Channel


class CategoryChannel(Channel):
    permission_overwrites: Optional[List[PermissionsOverwrite]] = list()
    """ List of permissions for category """
    name: str
    """ Name of category """
    nsfw: Optional[bool] = False
    """ Whether the category is marked as NSFW """
    position: int
    """ Position of category """
    guild_id: Snowflake
    """ ID of guild were category belongs """
