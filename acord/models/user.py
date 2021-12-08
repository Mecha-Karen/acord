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

    id: int  # TODO: Change this to ~acord.types.UserSnowflake~ later
    username: str  # the user's username, not unique across the platform
    discriminator: str  # the user's 4-digit discord-tag
    avatar: Optional[str]  # the user's avatar hash
    bot: Optional[bool]  # whether the user belongs to an OAuth2 application
    system: Optional[
        bool
    ]  # whether the user is an Official Discord System user (part of the urgent message system)
    mfa_enabled: Optional[
        bool
    ]  # whether the user has two factor enabled on their account
    banner: Optional[str]  # the user's banner hash
    accent_color: Optional[
        int
    ]  # the user's banner color encoded as an integer representation of hexadecimal color code
    locale: Optional[str]  # the user's chosen language option
    verified: Optional[bool]  # whether the email on this account has been verified
    flags: Optional[UserFlags]  # the flags on a user's account
    premium_type: Optional[int]  # the type of Nitro subscription on a user's account
    public_flags: Optional[UserFlags]  # the public flags on a user's account
    email: Optional[str]  # the user's email, can be None as bots cannot have an email

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
