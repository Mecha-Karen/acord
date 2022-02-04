from __future__ import annotations
from typing import Any, List, Literal, Optional
import pydantic

from acord.bases import Hashable, ApplicationFlags
from acord.models import Snowflake


class TeamMember(pydantic.BaseModel):
    membership_state: Literal[1, 2]
    """ the user's membership state on the team,
    were 1 is invited and 2 is accepted.
    """
    permissions: List[str]
    """ will always be ["*"] """
    team_id: Snowflake
    """ the id of the parent team of which they are a member """
    user: dict
    """ the avatar, discriminator, id, and username of the user """


class Team(pydantic.BaseModel, Hashable):
    icon: Optional[str]
    """ URL of the image of the team's icon """
    id: Snowflake
    """ the unique id of the team """
    members: List[TeamMember]
    """ the members of the team """
    name: str
    """ the name of the team """
    owner_user_id: Snowflake
    """ the user id of the current team owner """

    @pydantic.validator("icon")
    def _validate_guild_icon(cls, icon: str, **kwargs) -> Optional[str]:
        if not icon:
            return None

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/team-icons/{id}/{icon}.png.png"


class Application(pydantic.BaseModel, Hashable):
    id: Snowflake
    """ ID of the application """
    name: str
    """ the name of the app """
    icon: Optional[str]
    """ the icon hash of the app """
    description: str
    """ the description of the app """
    rpc_origins: Optional[List[pydantic.AnyHttpUrl]]
    """ an array of rpc origin urls, if rpc is enabled """
    bot_public: bool
    """ when false only app owner can join the app's bot to guilds """
    bot_require_code_grant: bool
    """ when true the app's bot will only join upon completion of the full oauth2 code grant flow """
    terms_of_service_url: Optional[pydantic.AnyHttpUrl]
    """ the url of the app's terms of service """
    privacy_policy_url: Optional[pydantic.AnyHttpUrl]
    """ the url of the app's privacy policy """
    owner: Optional[dict]
    """ partial user object containing info on the owner of the application """
    summary: str
    """ if this application is a game sold on Discord, 
    this field will be the summary field for the store page of its primary sku """
    verify_key: str
    """ the hex encoded key for verification in interactions and the GameSDK's GetTicket """
    team: Optional[Team]
    """ if the application belongs to a team, this will be a list of the members of that team """
    guild_id: Optional[Snowflake]
    """ if this application is a game sold on Discord, 
    this field will be the guild to which it has been linked """
    primary_sku_id: Optional[Snowflake]
    """ if this application is a game sold on Discord, 
    this field will be the id of the "Game SKU" that is created, 
    if exists """
    slug: Optional[str]
    """ if this application is a game sold on Discord, 
    this field will be the URL slug that links to the store page """
    cover_image: Optional[str]
    """ the application's default rich presence invite cover image hash """
    flags: Optional[ApplicationFlags]
    """ the application's public flags """

    @pydantic.validator("icon")
    def _validate_guild_icon(cls, icon: str, **kwargs) -> Optional[str]:
        if not icon:
            return None

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/app-icons/{id}/{icon}.png"
