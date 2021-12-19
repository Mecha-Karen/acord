from __future__ import annotations
from os import path

from typing import Any, List, Optional
import pydantic
import datetime
from acord.bases import Hashable
from acord.core.abc import Route
from acord.models import Snowflake

from .user import User

class Member(pydantic.BaseModel, Hashable):
    """
    Represents a guild member.

    Attributes
    ----------
    user: :class:`User`
        The User object of the member. Not included in MESSAGE_CREATE and MESSAGE_UPDATE events
    nick: :class:`str`
        Guild specific nickname of the member
    avatar: :class:`str`
        Member's guild avatar hash
    roles: List[:class:`Snowflake`]
        List of role IDs of roles the user has
    joined_at: :class:`datetime.datetime`
        The time the user joined the guild
    premium_since: :class:`datetime.datetime`
        When the user started boosting the guild
    deaf: :class:`bool`
        Whether if the member is deafened in voice channels
    mute: :class:`bool`
        Whether if the member is mutes in voice channels
    pending: :class:`bool`
        Whether if the member is pending verification. Not included in **NONE-GUILD-EVENTS** events
    permissions: :class:`str`
        Total permissions of the member in the channel. Including overwrites.
    guild_id: :class:`Snowflake`
        ID of the guild member is in
    """

    conn: Any # connection object

    user: Optional[User] # not included in MESSAGE_CREATE and MESSAGE_UPDATE events
    nick: Optional[str]
    avatar: Optional[str]
    roles: List[Snowflake]
    joined_at: datetime.datetime
    premium_since: Optional[datetime.datetime]
    deaf: bool
    mute: bool
    pending: Optional[bool] # not included in non-GUILD_ events
    permissions: Optional[str]
    guild_id: Snowflake

    async def ban(self, *, reason: str = None, delete_message_days: int = 0) -> None:
        """|coro|

        Bans this member from the guild

        Parameters
        ----------
        reason: :class:`str`
            Reason for banning member
        delete_message_days: :class:`int`
            An integer between 0-7, 
            deletes members messages within the past n days.
        """
        assert 0 <= delete_message_days <= 7, "Integer must be between 0-7"

        headers = dict({"Content-Type": "application/json"})

        if reason:
            headers.update({'X-Audit-Log-Reason': reason})
        data = dict(delete_message_days=delete_message_days)

        await self.conn.request(
            Route("PUT", path=f"/guilds/{self.guild_id}/bans/{self.user.id}"),
            headers=headers,
            data=data
        )
