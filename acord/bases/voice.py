from __future__ import annotations

import pydantic

from acord.models import Snowflake


class VoiceRegion(pydantic.BaseModel):
    id: Snowflake
    name: str
    optimal: bool
    depreciated: bool
    custom: bool
