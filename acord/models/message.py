from __future__ import annotations

import pydantic
import datetime

from acord.bases import Hashable, File
from acord.models import User

from typing import Any, List, Optional, Union


class Message(pydantic.BaseModel, Hashable):
    attachments: List[File]     
    author: User
    channel_id: int
    components: List[Any]
    content: str
    edited_timestamp: Optional[bool]
    embeds: List[Any]
    flags: int
    guild_id: int
    member: Any
    mention_everyone: bool
    mention_roles: List[Any]
    nonce: int
    pinned: bool
    referenced_message: Union[Message, Any]
    timestamp: datetime.datetime
    tts: bool
    type: int

    @pydantic.validator('timestamp')
    def _timestamp_validator(cls, timestamp):
        return datetime.datetime.fromisoformat(timestamp)
