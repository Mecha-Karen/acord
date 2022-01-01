from __future__ import annotations

import pydantic
import json
from acord.bases import Hashable, UserFlags
from acord.core.abc import Route
from typing import Any, List, Optional

from acord.models import Snowflake


class User(pydantic.BaseModel, Hashable):
    """
    Represents a Discord user.

    Attributes
    ----------
    id: :class:`acord.Snowflake`
        the user's id
    username: :class:`str`
        the user's username
    discriminator: :class:`str`
        the user's 4-digit discord-tag
    avatar: :class:`str`
        the url of the user's avatar
    bot: :class:`bool`
        The user is a bot or not
    system: :class:`bool`
        whether the user is an Official Discord System user
    mfa_enabled: :class:`bool`
        whether the user has two factor enabled on their account
    banner: :class:`str`
        the url of the user's banner, if they have one
    accent_colour: :class:`int`
        the user's banner color
    locale: :class:`str`
        the user's chosen language option
    verified: :class:`bool`
        whether the email on this account has been verified
    email: :class:`str`
        the user's email
    flags: :class:`acord.UserFlags`
        the user's account flags
    premium_type: :class:`int`
        the type of Nitro subscription on a user's account
    public_flags: :class:`acord.UserFlags`
        the public flags on a user's account
    """

    conn: Any  # Connection Object - For internal use

    id: int
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: Optional[bool]
    system: Optional[bool]
    mfa_enabled: Optional[bool]
    banner: Optional[str]
    accent_color: Optional[int]
    locale: Optional[str]
    verified: Optional[bool]
    flags: Optional[UserFlags]
    premium_type: Optional[int]
    public_flags: Optional[UserFlags] = 0
    email: Optional[str]

    dm_id: Optional[Snowflake]

    @pydantic.validator("avatar")
    def _validateEmail(cls, av: str, **kwargs) -> str:
        id = kwargs["values"]["id"]

        return f"https://cdn.discordapp.com/avatars/{id}/{av}.png"

    @pydantic.validator("banner")
    def _validateBanner(cls, banner: str, **kwargs) -> str:
        id = kwargs["values"]["id"]

        return f"https://cdn.discordapp.com/banners/{id}/{banner}.png"

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

    def mutual_guilds(self) -> List[Any]:
        """Return any guilds the user shares with the client"""
        return [i for i in self.conn.client.guilds if i.has_user(self)]

    def __str__(self) -> str:
        return f"{self.username}#{self.discriminator}"

    async def create_dm(self):
        """|coro|

        creates a DM with this user
        """
        from acord.models import DMChannel
        data = json.dumps({"recipient_id": self.id})

        r = await self.conn.request(
            Route("POST", path=f"/users/@me/channels"),
            data=data,
            headers={"Content-Type": "application/json"}
        )

        channel = DMChannel(conn=self.conn, **(await r.json()))
        self.conn.client.INTERNAL_STORAGE["channels"].update({channel.id: channel})

        self.dm_id = channel.id

        return channel

    async def send(self, **data) -> Any:
        """|coro|

        Automatically creates DM with user and sends message

        Parameters
        ----------
        all parameters are the same as :meth:`TextChannel.send`
        """
        if not self.dm_id:
            dm = await self.create_dm()
        else:
            dm = self.conn.client.get_channel(self.dm_id)

        return await dm.send(**data)
