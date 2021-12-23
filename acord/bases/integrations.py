from __future__ import annotations
from typing import Optional
from enum import IntEnum
import pydantic
import datetime

from acord.models import Snowflake, User


class IntegrationExpBehaviour(IntEnum):
    REMOVE_ROLE = 0
    KICK = 1


class IntegrationAccount(IntEnum):
    id: Snowflake
    name: str


class IntegrationApplication(pydantic.BaseModel):
    id: Snowflake
    name: str
    icon: str
    description: str
    summary: str
    bot: Optional[User]


class Integration(pydantic.BaseModel):
    id: Snowflake
    name: str
    type: str
    enabled: bool
    syncing: Optional[bool]
    role_id: Optional[Snowflake]
    enable_emoticons: Optional[bool]
    expire_behavior: Optional[IntegrationExpBehaviour]
    expire_grace_period: Optional[int]
    user: Optional[User]
    account: IntegrationAccount
    synced_at: Optional[datetime.datetime]
    subscriber_count: Optional[int]
    revoked: Optional[bool]
    application: Optional[IntegrationApplication]
