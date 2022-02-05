from __future__ import annotations

from typing import final
import datetime
from acord.core.abc import DISCORD_EPOCH


__all__ = (
    "Snowflake", 
    "PartialChannel", "PartialEmoji",
    "User",
    "Application",
    "Role", "RoleTags",
    "Emoji",
    "Sticker",
    "Attachment",
    "Member",
    "GuildScheduledEvent", "ScheduledEventUser", "ScheduledEventMetaData",
    "Message", "MessageReference", "WebhookMessage",
    "InteractionSlashOption", "InteractionData", "Interaction", "IMessageFlags",
    "Invite",
    "Channel", "TextChannel", "Stage", "Thread", "ThreadMeta", "ThreadMember",
    "VoiceChannel", "VoiceRegion", "CategoryChannel", "DMChannel", "GroupDMChannel",
    "IntegrationExpBehaviour", "IntegrationAccount", "IntegrationApplication", "PartialIntegration",
    "Integration", "AuditLogChange", "AuditLogEntryInfo", "AuditLogEntry", "AuditLog",
    "GuildTemplate", "Guild", "Ban", "GuildWidget", "GuildWidgetImageStyle", "WelcomeChannel",
    "WelcomeScreen",
)


@final
class Snowflake(int):
    """A concrete representation of a unique id for a discord model

    This object is a :class:`int` and only contains a few additional properties.
    """
    __slots__ = ()

    @property
    def created_at(self) -> datetime.datetime:
        """ When object was created """
        epoch = (self >> 22) / 1000
        epoch += DISCORD_EPOCH

        return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc)

    @property
    def internal_worker_id(self) -> int:
        """ ID of the worker that created snowflake. """
        return (self & 0x3E0_000) >> 17

    @property
    def internal_process_id(self) -> int:
        """ ID of the process that created snowflake. """
        return (self & 0x1F_000) >> 12

    @property
    def increment(self) -> int:
        """ Increment of when this object was made. """
        return self & 0xFFF


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
from .guild import (
    Guild, Ban, GuildWidget,
    GuildWidgetImageStyle,
    WelcomeChannel,
    WelcomeScreen,
)