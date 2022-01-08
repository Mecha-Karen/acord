from __future__ import annotations
from typing import Any, Optional

import pydantic
import datetime

from acord.bases import (
    Hashable, 
    ScheduledEventEntityType,
    ScheduledEventPrivacyLevel,
    ScheduledEventStatus
)
from acord.models import User, Snowflake


class ScheduledEventMetaData(pydantic.BaseModel):
    location: Optional[str]


class GuildScheduledEvent(pydantic.BaseModel, Hashable):
    conn: Any

    id: Snowflake
    """ the id of the scheduled event """
    guild_id: Snowflake
    """ the guild id the event belongs to """
    channel_id: Optional[Snowflake]
    """ the channel id the event will be hosted in """
    creator_id: Optional[Snowflake]
    """ the id of the user who created the event """
    name: str
    """ name of the scheduled event """
    description: Optional[str]
    """ description of event """
    scheduled_start_time: datetime.datetime
    """ the time the scheduled event will start """
    scheduled_end_time: Optional[datetime.datetime]
    """ the time the scheduled event will end """
    privacy_level: ScheduledEventPrivacyLevel
    """ the privacy level of the scheduled event """
    status: ScheduledEventStatus
    """ the status of the scheduled event """
    entity_type: ScheduledEventEntityType
    """ entity type of scheduled event """
    entity_id: Optional[Snowflake]
    """ the id of an entity associated with a guild scheduled event """
    entity_metadata: ScheduledEventMetaData
    """ additional metadata for the guild scheduled event """
    creator: Optional[User]
    """ the user that created the scheduled event """
    user_count: Optional[int]
    """ the number of users subscribed to the scheduled event """

    @pydantic.validator("creator")
    def _add_user_conn(cls, creator: Optional[User], **kwargs) -> Optional[User]:
        if not creator:
            return
        
        conn = kwargs["values"]["conn"]
        creator.conn = conn
        return creator
