from __future__ import annotations
import pydantic

from acord.bases import Hashable
from acord.models import Snowflake, User
from typing import Any, Optional


class Sticker(pydantic.BaseModel, Hashable):
    conn: Any

    id: Snowflake
    # ID of the sticker
    pack_id: Optional[Snowflake]
    # for standard stickers, id of the pack the sticker is from
    name: str
    # name of the sticker
    description: Optional[str]
    # description of the sticker
    tags: str
    # autocomplete/suggestion tags for the sticker (max 200 characters)
    asset: str
    # **DEPRECATED** previously the sticker asset hash, now an empty string
    type: int
    # type of sticker
    formate_type: int
    # type of sticker format
    available: Optional[bool]
    # whether this guild sticker can be used, may be false due to loss of Server Boosts
    guild_id: Optional[Snowflake]
    # id of the guild that owns this sticker
    user: Optional[User]
    # the user that uploaded the guild sticker
    sort_value: Optional[int]
    # the standard sticker's sort order within its pack
