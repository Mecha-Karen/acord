import pydantic
from typing import Optional


# https://discord.com/developers/docs/topics/teams#data-models-team-object
class Team(pydantic.BaseModel):
    icon: Optional[str]
    id: int
    members: object
    name: str
    owner_user_id: int
