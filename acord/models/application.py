import pydantic
from typing import Optional
from acord.models import User, Team


# https://discord.com/developers/docs/resources/application
class Application(pydantic.BaseModel):
    id: int
    name: str
    icon: Optional[str]
    description: str
    rpc_origins: Optional[list[str]]
    bot_public: bool
    bot_require_code_grant: bool
    terms_of_service_url: Optional[str]
    privacy_policy_url: str
    owner: User
    summary: str
    verify_key: str
    team: Team
    guild_id: Optional[int]
    primary_sku_id: int
    slug: int
    cover_image: str
    flags: Optional[int]

