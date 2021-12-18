from __future__ import annotations

import pydantic

from typing import Any, Optional
from acord.models import Snowflake, User, Guild


class GuildTemplate(pydantic.BaseModel):
    conn: Any

    code: str
    """ the template code (unique ID) """
    name: str
    """ template name """
    description: str
    """ the description for the template """
    usage_count: int
    """ number of times this template has been used """
    creator_id: Snowflake
    """ the ID of the user who created the template """
    creator: User
    """ the user who created the template """
    created_at: str
    """ when this template was created """
    updated_at: str
    """ when this template was last synced to the source guild """
    source_guild_id: Snowflake
    """ the ID of the guild this template is based on """
    serialized_source_guild: Guild
    """ the guild snapshot this template contains """
    is_dirty: Optional[bool]
    """ whether the template has unsynced changes """
