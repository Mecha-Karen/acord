from __future__ import annotations

import pydantic
from acord.bases import Hashable
from typing import Any, Optional


class User(pydantic.BaseModel, Hashable):
    conn: Any                   # Connection Object - For internal use

    id: int                     # TODO: Change this to ~acord.types.UserSnowflake~ later
    username: str               # the user's username, not unique across the platform
    discriminator: str          # the user's 4-digit discord-tag
    avatar: Optional[str]       # the user's avatar hash
    bot: Optional[bool]         # whether the user belongs to an OAuth2 application
    system: Optional[str]       # whether the user is an Official Discord System user (part of the urgent message system)
    mfa_enabled: Optional[bool] # whether the user has two factor enabled on their account
    banner: Optional[str]       # the user's banner hash
    accent_color: Optional[int] # the user's banner color encoded as an integer representation of hexadecimal color code
    locale: Optional[str]       # the user's chosen language option
    verified: Optional[bool]    # whether the email on this account has been verified
    flags: Optional[int]        # the flags on a user's account
    premium_type: Optional[int] # the type of Nitro subscription on a user's account
    public_flags: Optional[int] # the public flags on a user's account
    email: Optional[str]        # the user's email, can be None as bots cannot have an email

    @pydantic.validator('avatar')
    def _validateEmail(cls, av: str, **kwargs) -> str:
        id = kwargs['values']['id']

        return f'https://cdn.discordapp.com/avatars/{id}/{av}.png'

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
