import pydantic
from typing import Optional

from acord.models import Snowflake
from acord.bases import Hashable

class Attachment(pydantic.BaseModel, Hashable):
    id: Snowflake
    filename: str 
    description: Optional[str]
    content_type: Optional[str]
    size: int
    url: str
    proxy_url: str
    height: Optional[int]
    width: Optional[int]
    ephemeral: Optional[bool]

