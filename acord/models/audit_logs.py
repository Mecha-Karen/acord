from __future__ import annotations
from typing import Any, List, Optional
import pydantic

from acord.bases import Hashable, AuditLogEvent
from acord.models import (
    GuildScheduledEvent,
    Thread,
    User,
    PartialIntegration,
    Snowflake,
)
from acord.webhooks.webhook import Webhook


class AuditLogChange(pydantic.BaseModel):
    """\
    .. note::
        If :attr:`AuditLogChange.new_value`` is not present in the change object, 
        while :attr:`AuditLogChange.old_value`` is, 
        that means the property that was changed has been reset, 
        or set to ``None``
    """

    new_value: Optional[Any]
    """ new value of the key """
    old_value: Optional[Any]
    """ old value of the key """
    key: str
    """ name of audit log entry change,
    for full list of possible changes visit `me <https://discord.com/developers/docs/resources/audit-log#audit-log-change-object-audit-log-change-key>`_
    """


class AuditLogEntryInfo(pydantic.BaseModel):
    channel_id: Optional[Snowflake]
    """ channel in which the entities were targeted """
    count: Optional[int]
    """ number of entities targeted """
    delete_member_days: Optional[int]
    """ number of days after which inactive members were kicked """
    id: Optional[Snowflake]
    """ id of the overwritten entity """
    members_removed: Optional[int]
    """ number of members removed by the prune """
    message_id: Optional[Snowflake]
    """ id of the message that was targeted """
    role_name: Optional[str]
    """ name of the role if type is "0" (not present if type is "1") """
    type: Optional[str]
    """ type of overwritten entity - "0" for "role" or "1" for "member" """


class AuditLogEntry(pydantic.BaseModel, Hashable):
    target_id: Optional[str]
    """ ID of affected entity,
    can be an ID of anything implementing the :class:`Hashable` class. """
    changes: Optional[List[AuditLogChange]]
    """ list of changes made to target """
    user_id: Optional[Snowflake]
    """ the user who made changes

    .. warning::
        If your attempting to use this value for user who invoked command,
        you will instead recieve the client.
    """
    id: Snowflake
    """ ID of entry """
    action_type: AuditLogEvent
    """ type of action made """
    options: Optional[AuditLogEntryInfo]
    """ additional info for certain action types """
    reason: Optional[str]
    """ the reason for the change """


class AuditLog(pydantic.BaseModel):
    conn: Any

    guild_id: Snowflake
    audit_log_entries: List[AuditLogEntry]
    guild_scheduled_events: List[GuildScheduledEvent]
    integrations: List[PartialIntegration]
    threads: List[Thread]
    users: List[User]
    webhooks: List[Webhook]

    @pydantic.validator(
        "guild_scheduled_events", "integrations", "threads", "users", "webhooks"
    )
    def _validate_conns(cls, _, **kwargs):
        conn = kwargs["values"]["conn"]

        if isinstance(_, Webhook):
            _.__connection__ = conn
        if isinstance(_, list):
            for i in _:
                i.conn = conn
        else:
            _.conn = conn
        return _
