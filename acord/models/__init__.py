from typing import TypeVar

Snowflake = TypeVar("Snowflake", bound=int)
# Simple snowflake object

from .partials import PartialChannel, PartialEmoji
from .user import User
from .application import Application
from .roles import Role, RoleTags
from .emoji import Emoji
from .sticker import Sticker
from .attachment import Attachment
from .member import Member
from .guild_sched_event import (
    GuildScheduledEvent,
    ScheduledEventUser,
    ScheduledEventMetaData,
)
from .message import Message, MessageReference, WebhookMessage
from .interaction import (
    InteractionSlashOption,
    InteractionData,
    Interaction,
    IMessageFlags,
)
from .invite import Invite
from .channels import (
    Channel,
    TextChannel,
    Stage,
    Thread,
    ThreadMeta,
    ThreadMember,
    VoiceChannel,
    VoiceRegion,
    CategoryChannel,
    DMChannel,
    GroupDMChannel,
)
from .integrations import (
    IntegrationExpBehaviour,
    IntegrationAccount,
    IntegrationApplication,
    PartialIntegration,
    Integration,
)
from .audit_logs import AuditLogChange, AuditLogEntryInfo, AuditLogEntry, AuditLog
from .guild_template import GuildTemplate
from .guild import Guild, Ban
