import pydantic
from typing import Optional

from acord.models import Snowflake
from acord.bases import Hashable

class Attachment(pydantic.BaseModel, Hashable):
    id: Snowflake
    """
    ID of the attachment
    """
    filename: str
    """
    Name of the attached file
    """
    description: Optional[str]
    """
    Description of the file
    """
    content_type: Optional[str]
    """
    Media type of the attachment
    """
    size: int
    """
    Size of the attachment, in bytes
    """
    url: str
    """
    Source URL of the file
    """
    proxy_url: str
    """
    A proxied URL of the file
    """
    height: Optional[int]
    """
    Height of the file (if it's an image)
    """
    width: Optional[int]
    """
    Width of the file (if its an image)
    """
    ephemeral: Optional[bool]
    """
    Whether the file is ephemeral
    """

