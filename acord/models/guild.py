from __future__ import annotations

from typing import Any, List, Optional
import pydantic
import datetime

from acord.core.abc import Route, isInt, DISCORD_EPOCH
from acord.bases import Hashable
from acord.models import Snowflake


class Guild(pydantic.BaseModel, Hashable):
    id: Snowflake
    name: str
    icon: str

    afk_channel_id: Optional[Snowflake]
    afk_timeout: Optional[int]
    
