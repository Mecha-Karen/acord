from __future__ import annotations
from typing import Any, List, Optional
import pydantic
import datetime

from acord.bases import Hashable
from acord.core.abc import Route
from acord.models import Snowflake, Role
from acord.utils import _payload_dict_to_json

from .user import User


class MemberVoiceState(pydantic.BaseModel):
    guild_id: Optional[Snowflake]
    channel_id: Optional[Snowflake]
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    self_stream: Optional[bool]
    self_video: bool
    suppress: bool
    request_to_speak_timestamp: Optional[datetime.datetime]


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

    conn: Any  # connection object

    user: Optional[User]  # not included in MESSAGE_CREATE and MESSAGE_UPDATE events
    nick: Optional[str]
    avatar: Optional[str]
    roles: List[Snowflake]
    joined_at: datetime.datetime
    premium_since: Optional[datetime.datetime]
    deaf: bool
    mute: bool
    pending: Optional[bool]  # not included in non-GUILD_ events
    permissions: Optional[str]
    guild_id: Snowflake
    voice_state: Optional[MemberVoiceState]

    @pydantic.validator("user")
    def _validate_user(cls, user, **kwargs):
        conn = kwargs["values"]["conn"]
        user.conn = conn

        return user

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
            headers.update({"X-Audit-Log-Reason": reason})
        data = dict(delete_message_days=delete_message_days)

        await self.conn.request(
            Route("PUT", path=f"/guilds/{self.guild_id}/bans/{self.user.id}"),
            headers=headers,
            data=data,
        )

    async def kick(self, *, reason: str = None) -> None:
        """|coro|

        Kicks this member from the guild

        Parameters
        ----------
        reason: :class:`str`
            Reason for kicking member
        """
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.conn.request(
            Route("DELETE", path=f"/guilds/{self.guild_id}/members/{self.user.id}"),
            headers=headers,
        )

    async def edit(self, *, reason: str = None, **data) -> Member:
        """|coro|

        Modifies current member

        Parameters
        ----------
        nick: :class:`str`
            New nickname for user
        roles: :class:`str`
            New roles for members,
            roles will be updated exactly as provided.
            If you wish to keep existing roles, use :meth:`Member.add_role`.
        mute: :class:`bool`
            whether the user is muted in voice channels.
            Raises BadRequest if user is not in a VC.
        deaf: :class:`bool`
            whether the user is deafened in voice channels.
            Raises BadRequest if user is not in a VC.
        channel_id: :class:`Snowflake`
            id of channel to move user to (if they are connected to voice).
        communication_disabled_until: :obj:`py:datetime.datetime`
            User communication timeout.
            If set to ``None``, removes timeout.
        """
        from acord.payloads import MemberEditPayload

        payload = _payload_dict_to_json(MemberEditPayload, **data)
        headers = dict({"Content-Type": "application/json"})

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        r = await self.conn.request(
            Route("PATCH", path=f"/guilds/{self.guild_id}/members/{self.user.id}"),
            headers=headers,
            data=payload,
        )

        member = Member(guild_id=self.guild_id, conn=self.conn, **(await r.json()))
        guild = self.conn.client.get_guild(member.guild_id)
        guild.members.update({member.id: member})

        return member

    async def add_role(self, role: Role, *, reason: str = None) -> None:
        """|coro|

        Adds a single role to user, for more roles consider using:

        * :meth:`Member.edit`
        * :meth:`Member.add_roles`

        Parameters
        ----------
        role: :class:`Role`
            Role to add to user
        reason: :class:`str`
            Reason for adding role
        """
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.conn.request(
            Route(
                "PUT",
                path=f"/guilds/{self.guild_id}/members/{self.user.id}/roles/{role.id}",
            ),
            headers=headers,
        )

        if role not in self.roles:
            self.roles.append(role)

    async def add_roles(self, *roles, reason: str = None) -> Member:
        """|coro|

        Adds many roles to the member in one go,
        utility method for :meth:`Member.edit`.

        Parameters
        ----------
        *roles: :class:`Role`
            Roles to be updated,
            must be provided individually as args!
        reason: :class:`str`
            Reason for adding roles
        """
        n_roles = self.roles

        for role in roles:
            if role not in n_roles:
                n_roles.append(role)

        return await self.edit(roles=n_roles, reason=reason)

    async def remove_role(self, role: Role, *, reason: str = None) -> None:
        """|coro|

        Remove a role from member

        Parameters
        ----------
        role: :class:`Role`
            Role to remove
        reason: :class:`str`
            Reason for removing role
        """
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.conn.request(
            Route(
                "DELETE",
                path=f"/guilds/{self.guild_id}/members/{self.user.id}/roles/{role.id}",
            ),
            headers=headers,
        )

        if role in self.roles:
            self.roles.remove(role)

    async def remove_roles(self, *roles, reason: str = None) -> Member:
        """|coro|

        Removes many roles from the member in one go,
        utility method for :meth:`Member.edit`.

        Parameters
        ----------
        *roles: :class:`Role`
            Roles to be updated,
            must be provided individually as args!
        reason: :class:`str`
            Reason for removing roles
        """
        n_roles = self.roles

        for role in roles:
            if role in n_roles:
                n_roles.remove(role)

        return await self.edit(roles=n_roles, reason=reason)
