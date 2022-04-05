from __future__ import annotations
from pydantic import AnyHttpUrl
from typing import Any, List, Optional

from acord.models import Snowflake, User
from .base import Channel
from .textExt import ExtendedTextMethods


class DMChannel(Channel, ExtendedTextMethods):
    conn: Any
    last_message_id: Optional[Snowflake]
    """ ID of last message sent in channel """
    recipients: List[User]
    """ List of users in channel, usually just 1 user """


class GroupDMChannel(DMChannel):
    icon: Optional[AnyHttpUrl]
    """ Icon of the group DM """
    owner_id: Snowflake
    """ ID of group owner """
