from __future__ import annotations

import pydantic
from acord.bases import Hashable, UserFlags
from typing import Any, List, Optional
import datetime

from .user import User

class Member(pydantic.BaseModel, Hashable):
    """
    Represents a guild member.

    Attributes
    ----------
    user: :class:`acord.models.User`
          The User object of the member. Not included in MESSAGE_CREATE and MESSAGE_UPDATE events
    nick: :class:`str`
          Guild specific nickname of the member
    avatar: :class:`str`
          Member's guild avatar hash
    roles: :class:`List[Snowflake]`
          List of role IDs of roles the user has
    joined_at: :class:`datetime.datetime`
          The time the user joined the guild
    premium_since: :class:`datetime.datetime`
          When the user started boosting the guild
    deaf: :class:`bool`
          Whether if the member is deafened in voice channels
    mute: :class:`bool`
          Whether if the member is mutes in voice channels
    pending: :class:`bool`
          Whether if the member is pending verification. Not included (False) in non-GUILD_\* events
    permissions: :class:`str`
          Total permissions of the member in the channel. Including overwrites.
    """
    # Please check the doc strings before merging @Seniatical
    # and tell me if i need to add anything else :)

    con: Any # connection object

    user: Optional[User] # not included in MESSAGE_CREATE and MESSAGE_UPDATE events

    nick: Optional[str]
    avatar: Optional[str]
    roles: List[Snowflake]
    joined_at: datetime.datetime
    premium_since: Optional[datetime.datetime]
    deaf: bool
    mute: bool
    pending: Optional[bool] # not included in non-GUILD_ events
    permissions: Optional[str]
