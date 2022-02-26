from __future__ import annotations
import re
from typing import Any, List, Optional
import pydantic
import datetime

from acord.bases import Hashable
from acord.core.abc import Route
from acord.models import Snowflake
from .user import User


class StageInstanceInvite(pydantic.BaseModel, Hashable):
    members: List[Any]
    participant_count: int
    speaker_count: int
    topic: str


class Invite(pydantic.BaseModel, Hashable):
    conn: Any  # Connection object - For internal use

    code: str
    """the invite code (unique ID)"""
    guild_id: Optional[Snowflake]
    """the guild this invite is for"""
    channel_id: Snowflake
    """the channel this invite is for"""
    inviter: Optional[User]
    """the user who created the invite"""
    target_type: Optional[int]
    """the type of target for this voice channel invite"""
    target_user: Optional[User]
    """the user whose stream to display for this voice channel stream invite"""
    target_application: Optional[Any]
    """the embedded application to open for this voice channel embedded application invite"""
    approximate_presence_count: Optional[int]
    """approximate count of online members"""
    approximate_member_count: Optional[int]
    """approximate count of total members"""
    expires_at: Optional[datetime.datetime]
    """the expiration date of this invite"""
    stage_instance: Optional[StageInstanceInvite]
    """stage instance data if there is a public Stage instance in the Stage channel this invite is for"""

    @classmethod
    async def from_code(cls, client, code: str, **params) -> Invite:
        """|coro|

        Creates a new invite from its code,
        fetches from API.

        .. warning::
            This will return an object without a conn parameters,
            so methods like :meth:`Invite.delete` will not function.

        Parameters
        ----------
        client: :class:`Client`
            client being used to fetch invite
        code: :class:`str`
            code of invite to fetch
        with_counts: :class:`bool`
            whether the invite should contain approximate member counts
        with_expiration: :class:`bool`
            whether the invite should contain the expiration date
        guild_scheduled_event_id: :class:`bool`
            the guild scheduled event to include with the invite
        """
        params = {k: str(v).lower() for k, v in params.items()}

        async with client.http.request(
            Route("GET", path=f"/invites/{code}")
        ) as r:
            return cls(conn=client.http, **(await r.json()))

    async def delete(self, *, reason: str) -> None:
        """|coro|

        Deletes this invite

        Parameters
        ----------
        reason: :class:`str`
            Reason for deleting invite
        """
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.conn.request(
            Route("DELETE", path=f"/invites/{self.code}"), headers=headers
        )
