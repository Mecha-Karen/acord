from __future__ import annotations
from typing import Any, Dict, Optional
import pydantic

from acord.bases import Hashable, Permissions, Color
from acord.core.abc import Route
from acord.utils import _payload_dict_to_json
from acord.models import Snowflake


class RoleTags(pydantic.BaseModel):
    bot_id: Optional[Snowflake]
    integration_id: Optional[Snowflake]
    premium_subscriber: Optional[Any]


class Role(pydantic.BaseModel, Hashable):
    conn: Any

    id: int
    """ Role ID """
    name: str
    """ Name of role """
    color: Color
    """ Colour of role """
    hoist: bool
    """ Role is pinned in the user listing """
    icon: Optional[str]
    """ Role icon URL """
    unicode_emoji: Optional[str]
    """ Role unicode emoji """
    position: int
    """ Role position """
    permissions: Permissions
    """ Role permissions """
    managed: bool
    """ Whether this role is managed by an integration """
    mentionable: bool
    """ Whether role can be mentioned """
    tags: Optional[RoleTags]
    """ Role tags """
    guild_id: int
    """ Guild ID of role """

    @pydantic.validator("icon")
    def _validate_guild_icon(cls, role_icon: str, **kwargs) -> Optional[str]:
        if not role_icon:
            return None

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/role-icons/{id}/{role_icon}.png"

    @pydantic.validator("permissions", pre=True)
    def _validate_permissions(cls, permissions: str):
        if not permissions:
            return 0
        return int(permissions)

    async def edit(self, *, reason: str = None, **data) -> Role:
        """|coro|

        Edits guild role

        Parameters
        ----------
        name: :class:`str`
            name for role
        permissions: :class:`Permissions`
            enabled/disabled permissions
        color: :class:`Color`
            Colour of the role
        hoist: :class:`bool`
            whether the role should be displayed separately in the sidebar
        icon: :class:`File`
            the role's icon image
        unicode_emoji: :class:`str`
            role's unicode emoji
        mentionable: :class:`bool`
            whether the role should be mentionable
        reason: :class:`str`
            Reason for deleting role
        """
        from acord.payloads import RoleEditPayload

        headers = dict({"Content-Type": "application/json"})

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        payload = _payload_dict_to_json(RoleEditPayload, **data)

        r = await self.conn.request(
            Route("PATCH", path=f"/guilds/{self.guild_id}/roles/{self.id}"),
            headers=headers,
            data=payload,
        )

        role = Role(**(await r.json()))
        (self.conn.get_guild(self.guild_id)).roles.update({role.id: role})

        return role

    async def delete(self, *, reason: str = None):
        """|coro|

        Deletes role from guild

        Parameters
        ----------
        reason: :class:`str`
            Reason for deleting role
        """
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.conn.request(
            Route("DELETE", path=f"/guilds/{self.guild_id}/roles/{self.id}"),
            headers=headers,
        )
        (self.conn.get_guild(self.guild_id)).roles.pop(self.id)
