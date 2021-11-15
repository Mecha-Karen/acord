import pydantic
from typing import Optional


# https://discord.com/developers/docs/resources/user#get-user
class User(pydantic.BaseModel):
    id: int # Change this to ~acord.snowflakes.UserSnowflake~ later
    username: str # the user's username, not unique across the platform
    discriminator: str # the user's 4-digit discord-tag
    avatar: Optional[str] # the user's avatar hash
    bot: bool # whether the user belongs to an OAuth2 application
    system: Optional[bool] # whether the user is an Official Discord System user (part of the urgent message system)
    mfa_enabled: bool # whether the user has two factor enabled on their account
    banner: Optional[str] # the user's banner hash
    accent_color: Optional[int] # the user's banner color encoded as an integer representation of hexadecimal color code
    locale: Optional[str] # the user's chosen language option
    verified: bool # whether the email on this account has been verified
    email: Optional[str] # the user's email
    flags: Optional[int] # the flags on a user's account
    premium_type: Optional[int] # the type of Nitro subscription on a user's account
    public_flags: Optional[int] # the public flags on a user's account
