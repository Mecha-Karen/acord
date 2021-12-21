from typing import List, Optional, TypeVar

Snowflake = TypeVar("Snowflake", bound=int)

# Simple snowflake object

from .user import User
from .roles import Role, RoleTags
from .emoji import Emoji
from .sticker import Sticker
from .attachment import Attachment
from .message import Message, MessageReference
from .member import Member
from .invite import Invite
from .channels import (
    Channel,
    TextChannel,
    Stage,
    Thread,
    ThreadMeta,
    ThreadMember,
    VoiceChannel,
    CategoryChannel,
    DMChannel,
    GroupDMChannel,
)
from .guild import Guild, Ban
from .guild_template import GuildTemplate

Message.update_forward_refs()

TextChannel.fetch_invites.__annotations__["return"] = List[Invite]
TextChannel.create_invite.__annotations__["return"] = List[Invite]
Invite.__annotations__["guild"] = Optional[Guild]
