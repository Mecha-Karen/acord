from __future__ import annotations
from typing import Any, List, Optional
import pydantic

from acord.bases import Hashable, ApplicationFlags
from acord.models import Snowflake, User


class TeamMember(pydantic.BaseModel):
    membership_state: int
    permissions: List[str]
    team_id: Snowflake
    user: User


class Team(pydantic.BaseModel, Hashable):
    icon: Optional[str]
    id: Snowflake
    members: List[TeamMember]
    name: str
    owner_user_id: Snowflake

    @pydantic.validator("icon")
    def _validate_guild_icon(cls, icon: str, **kwargs) -> Optional[str]:
        if not icon:
            return None

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/team-icons/{id}/{icon}.png.png"


class Application(pydantic.BaseModel, Hashable):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str
    rpc_origins: Optional[List[pydantic.AnyHttpUrl]]
    bot_public: bool
    bot_require_code_grant: bool
    terms_of_service_url: Optional[pydantic.AnyHttpUrl]
    privacy_policy_url: Optional[pydantic.AnyHttpUrl]
    owner: Optional[User]
    summary: str
    verify_key: str
    team: Optional[Team]
    guild_id: Optional[Snowflake]
    primary_sku_id: Optional[Snowflake]
    slug: Optional[str]
    cover_image: Optional[str]
    flags: Optional[ApplicationFlags]


    @pydantic.validator("icon")
    def _validate_guild_icon(cls, icon: str, **kwargs) -> Optional[str]:
        if not icon:
            return None

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/app-icons/{id}/{icon}.png"

