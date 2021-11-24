from typing import TypeVar, Union

Snowflake = TypeVar("Snowflake", bound=int)

# Simple snowflake object

from .user import User
from .emoji import Emoji
from .message import Message

Message.update_forward_refs()
