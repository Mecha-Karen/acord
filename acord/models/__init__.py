from typing import TypeVar

Snowflake = TypeVar("Snowflake", bound=int)

# Simple snowflake object

from .user import User
from .emoji import Emoji

from .message import Message, MessageReference
from .channels import Channel, TextChannel
from .guild import Guild

Message.update_forward_refs()
