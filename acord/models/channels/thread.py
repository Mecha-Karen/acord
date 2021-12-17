from __future__ import annotations
from typing import Any, Optional

import pydantic
import datetime

from acord.bases import Hashable
from acord.core.abc import Route
from acord.models import Snowflake, Member

from .base import Channel


class ThreadMeta(pydantic.BaseModel):
    archived: bool
    archive_timestamp: datetime.datetime
    auto_archive_duration: int
    locked: bool
    invitable: Optional[bool]


class ThreadMember(pydantic.BaseModel):
    id: Snowflake


class Thread(Channel):
    conn: Any

    id: Snowflake
    """ Thread id """
    guild_id: Snowflake
    """ Guild id of were thread belongs """
    parent_id: Snowflake
    """ Channel id of were thread was created from """
    owner_id: Snowflake
    """ Id of user who created this thread """
    name: str
    """ Name of thread """
    last_message_id: Optional[Snowflake]
    """ Last message sent in thread """
    last_pin_timestamp: Optional[datetime.datetime]
    """ Last pinned message in thread """
    rate_limit_per_user: Optional[int]
    """ amount of seconds a user has to wait before sending another message """
    message_count: Optional[int]
    """ approx amount of message in thread, stops counting after 50 """
    member_count: Optional[int]
    """ aprox members in thread, stops counting after 50 """
    thread_metadata: ThreadMeta
    """ Additional data about thread """

    async def join(self) -> None:
        """|coro|

        Joins current thread
        """
        await self.conn.request(Route("PUT", path=f'/channels/{self.parent_id}/thread-members/@me'))
