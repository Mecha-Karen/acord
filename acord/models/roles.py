from __future__ import annotations
from typing import Any, Dict, Optional
import pydantic

from acord.bases import Hashable, Permissions
from acord.bases.embeds import Color

from acord.models import Snowflake


class RoleTags(pydantic.BaseModel):
    bot_id: Optional[Snowflake]
    integration_id: Optional[Snowflake]
    premium_subscriber: Optional[Any]


class Role(pydantic.BaseModel, Hashable):
    conn: Any

    id: int
    """ Role ID """
    name: str
    """ Name of role """
    color: Color
    """ Colour of role """
    hoist: bool
    """ Role is pinned in the user listing """
    icon: Optional[str]
    """ Role icon URL """
    unicode_emoji: Optional[str]
    """ Role unicode emoji """
    position: int
    """ Role position """
    permissions: Permissions
    """ Role permissions """
    managed: bool
    """ Whether this role is managed by an integration """
    mentionable: bool
    """ Whether role can be mentioned """
    tags: Optional[RoleTags]
    """ Role tags """
    guild_id: int
    """ Guild ID of role """

    @pydantic.validator("icon")
    def _validate_guild_icon(cls, role_icon: str, **kwargs) -> Optional[str]:
        if not role_icon:
            return None

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/role-icons/{id}/{role_icon}.png"
