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
from acord.utils import _payload_dict_to_json


class ScheduledEventMetaData(pydantic.BaseModel):
    location: Optional[str]
    """ location were event will take place """


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

    async def edit(self, *, reason: str = None, **data) -> GuildScheduledEvent:
        """|coro|

        Edits a scheduled event,
        to start or end an event use this method.

        Parameters
        ----------
        reason: :class:`str`
            reason for editting event
        entity_type: :class:`ScheduledEventEntityType`
            the entity type of the scheduled event
        name: :class:`str`
            name of the event
        channel_id: :class:`Snowflake`
            the channel id of the scheduled event.
        entity_metadata: :class:`ScheduledEventMetaData`
            the entity metadata of the scheduled event
        privacy_level: :class:`ScheduledEventPrivacyLevel`
            the privacy level of the scheduled event
        scheduled_start_time: :class:`datetime.datetime`
            the start time of the scheduled event
        scheduled_end_time: :class:`datetime.datetime`
            the end time of the scheduled event
        description: :class:`str`
            the description of the scheduled event
        status: :class:`ScheduledEventStatus`
            the status of the scheduled event
        """
        from acord.payloads import ScheduledEventEditPayload

        headers = {"Content-Type": "application/json"}

        if reason is not None:
            headers["X-Audit-Log-Reason"] = reason

        r = await self.conn.request(
            Route("PATCH", path=f"/guilds/{self.guild_id}/scheduled-events/{self.id}"),
            headers=headers,
            data=_payload_dict_to_json(ScheduledEventEditPayload, **data)
        )

        return GuildScheduledEvent(conn=self.conn, **(await r.json()))

