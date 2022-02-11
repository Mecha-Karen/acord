# Partials are basically any object which requires objects from
# acord.models
# But are not actual recourses

from __future__ import annotations

import pydantic

from acord.bases import Hashable, ChannelTypes
from acord.models import Snowflake


class PartialEmoji(pydantic.BaseModel, Hashable):
    id: Snowflake
    name: str
    animated: bool


class PartialChannel(pydantic.BaseModel):
    name: str
    type: ChannelTypes
