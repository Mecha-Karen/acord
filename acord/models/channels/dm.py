from __future__ import annotations
from pydantic import AnyHttpUrl
from typing import List, Optional

from acord.models import Snowflake, User
from .base import Channel
from .textExt import ExtendedTextMethods


class DMChannel(Channel, ExtendedTextMethods):
    last_message_id: Snowflake
    """ ID of last message sent in channel """
    recipients: List[User]
    """ List of users in channel, usually just 1 user """


class GroupDMChannel(DMChannel):
    icon: Optional[AnyHttpUrl]
    owner_id: Snowflake
