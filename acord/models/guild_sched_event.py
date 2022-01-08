from __future__ import annotations
from typing import Any, Iterator, List, Optional

import pydantic
import datetime

from acord.bases import (
    Hashable, 
    ScheduledEventEntityType,
    ScheduledEventPrivacyLevel,
    ScheduledEventStatus
)
from acord.core.abc import Route
from acord.models import User, Member, Snowflake


class ScheduledEventMetaData(pydantic.BaseModel):
    location: Optional[str]


class ScheduledEventUser(pydantic.BaseModel):
    guild_scheduled_event_id: Snowflake
    """ the scheduled event id which the user subscribed to """
    user: User
    """ user which subscribed to an event """
    member: Optional[Member]
    """ guild member for this user for the guild which this event belongs to, 
    if any """


class GuildScheduledEvent(pydantic.BaseModel, Hashable):
    conn: Any

    id: Snowflake
    """ the id of the scheduled event """
    guild_id: Snowflake
    """ the guild id the event belongs to """
    channel_id: Optional[Snowflake]
    """ the channel id the event will be hosted in """
    creator_id: Optional[Snowflake]
    """ the id of the user who created the event """
    name: str
    """ name of the scheduled event """
    description: Optional[str]
    """ description of event """
    scheduled_start_time: datetime.datetime
    """ the time the scheduled event will start """
    scheduled_end_time: Optional[datetime.datetime]
    """ the time the scheduled event will end """
    privacy_level: ScheduledEventPrivacyLevel
    """ the privacy level of the scheduled event """
    status: ScheduledEventStatus
    """ the status of the scheduled event """
    entity_type: ScheduledEventEntityType
    """ entity type of scheduled event """
    entity_id: Optional[Snowflake]
    """ the id of an entity associated with a guild scheduled event """
    entity_metadata: ScheduledEventMetaData
    """ additional metadata for the guild scheduled event """
    creator: Optional[User]
    """ the user that created the scheduled event """
    user_count: Optional[int]
    """ the number of users subscribed to the scheduled event """

    @pydantic.validator("creator")
    def _add_user_conn(cls, creator: Optional[User], **kwargs) -> Optional[User]:
        if not creator:
            return
        
        conn = kwargs["values"]["conn"]
        creator.conn = conn
        return creator

    async def delete(self) -> None:
        """|coro|

        Deletes this event
        """
        await self.conn.request(
            Route("DELETE", path=f"/guilds/{self.guild_id}/scheduled-events/{self.id}")
        )


    @pydantic.validate_arguments
    async def fetch_users(self, *,
        limit: int = 100,
        with_member: bool = False,
        before: Snowflake = None,
        after: Snowflake = None
    ) -> Iterator[ScheduledEventUser]:
        """|coro|

        Fetches members who have joined this event

        Parameters
        ----------
        limit: :class:`int`
            How many members to fetch
        with_member: :class:`bool`
            :attr:`ScheduledEventUser.member` will contain a member object,
            of who suscribed to the event
        before: :class:`Snowflake`
            consider only users before given user id
        after: :class:`Snowflake`
            consider only users after given user id
        """
        r = await self.conn.request(
            Route(
                "GET", 
                path=f"/guilds/{self.guild_id}/scheduled-events/{self.id}/users",
                limit=limit,
                with_member=str(with_member).lower(),
                before=before,
                after=after
                )
        )

        for sched_user in (await r.json()):
            u = User(conn=self.conn, **sched_user["user"])

            if with_member:
                m = Member(conn=self.conn, user=u, **sched_user["member"])
            else:
                m = None

            yield ScheduledEventUser(guild_scheduled_event_id=self.id, user=u, member=m)
