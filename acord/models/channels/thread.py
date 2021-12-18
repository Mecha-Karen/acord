from __future__ import annotations
from typing import Any, Dict, Iterator, List, Literal, Optional, Union

import pydantic
import datetime

from acord.core.abc import Route
from acord.models import Snowflake, Member

from .base import Channel
from .textExt import ExtendedTextMethods


class ThreadMeta(pydantic.BaseModel):
    archived: bool
    """Whether the thread has been archived"""
    archive_timestamp: datetime.datetime
    """Time of when thread was archived"""
    auto_archive_duration: int
    """Time for thread to be auto archived"""
    locked: bool
    """Whether this thread has been locked"""
    invitable: Optional[bool]
    """Whether this thread is invite only"""


class ThreadMember(pydantic.BaseModel):
    id: Snowflake
    """ID of thread"""
    user_id: Snowflake
    """ID of user in thread"""
    join_timestamp: datetime.datetime
    """When did this user join this thread"""
    flags: int
    """Thread member flags"""


class Thread(Channel, ExtendedTextMethods):
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

    members: Dict[Snowflake, ThreadMember] = dict()
    """ Mapping of members in thread, fills with each fetch """

    async def join(self) -> None:
        """|coro|

        Joins current thread
        """
        await self.add_member(member="@me")

    async def leave(self) -> None:
        """|coro|

        Leaves current thread
        """
        await self.remove_member(member="@me")

    async def add_member(self, *, member: Union[Member, Snowflake]) -> None:
        """|coro|
        
        Adds a member to the thread

        Parameters
        ----------
        member: Union[:class:`Member`, :class:`Snowflake`]
        """
        if member != "@me":
            member = member.id

        await self.conn.request(Route("PUT", path=f'/channels/{self.id}/thread-members/{member}'))

    async def remove_member(self, *, member: Union[Member, Snowflake]) -> None:
        """|coro|

        Removes a member from the thread

        Parameters
        ----------
        member: Union[:class:`Member`, :class:`Snowflake`]
        """
        if isinstance(member, Union[Member, Snowflake]):
            member = member.id

        await self.conn.request(Route("DELETE", path=f'/channels/{self.id}/thread-members/{member}'))
        self.members.pop(member, None)

    async def fetch_member(
        self, 
        *, 
        member: Union[Member, Snowflake],
        as_guild_member: bool = False
        ) -> Optional[Union[ThreadMember, Member]]:
        """|coro|

        Fetches member from thread

        Parameters
        ----------
        member: Union[:class:`Member`, :class:`Snowflake`]
            Member to fetch
        as_guild_member: :class:`bool`
            whether to return the fetched member as a :class:`ThreadMember` object or :class:`Member`
        """
        if isinstance(member, Member):
            member = member.id

        r = await self.conn.request(
            Route("GET", path=f'/channels/{self.id}/thread-members/{member}')
        )

        tmember = ThreadMember(**(await r.json()))
        self.members.update({member.user_id: tmember})

        if not as_guild_member:
            member = tmember
        else:
            id = (await r.json())['user_id']
            guild = self.conn.client.get_guild(self.guild_id)
            member = guild.get_member(id)

        return member

    async def fetch_members(
        self, 
        *, 
        as_guild_member: bool = False
        ) -> Iterator[Union[Member, ThreadMember]]:
        """|coro|

        Fetches all members in the thread

        Parameters
        ----------
        as_guild_member: :class:`bool`
            Whether to return the thread members as :class:`ThreadMember` or :class:`Member`
        """
        r = await self.conn.request(
            Route("GET", path=f'/channels/{self.id}/thread-members')
        )
        members = await r.json()
        guild = self.conn.client.get_guild(self.guild_id)

        for member in members:
            nmember = ThreadMember(**member)
            self.members.update({nmember.user_id: nmember})

            if as_guild_member:
                id = member['user_id']
                yield guild.get_member(id)
            else:
                yield nmember
