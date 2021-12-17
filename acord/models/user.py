from __future__ import annotations

import pydantic
from acord.bases import Hashable, UserFlags
from typing import Any, List, Optional


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
    system: Optional[
        bool
    ]
    mfa_enabled: Optional[
        bool
    ]
    banner: Optional[str]
    accent_color: Optional[
        int
    ]
    locale: Optional[str]
    verified: Optional[bool]
    flags: Optional[UserFlags]
    premium_type: Optional[int]
    public_flags: Optional[UserFlags] = 0
    email: Optional[str]

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
        return f'{self.username}#{self.discriminator}'
