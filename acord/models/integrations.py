from __future__ import annotations
from typing import Any, Optional
from enum import IntEnum
import pydantic
import datetime
from acord.bases.mixins import Hashable

from acord.models import User, Snowflake
from acord.core.abc import Route


class IntegrationExpBehaviour(IntEnum):
    REMOVE_ROLE = 0
    KICK = 1


class IntegrationAccount(pydantic.BaseModel, Hashable):
    id: Snowflake
    name: str


class IntegrationApplication(pydantic.BaseModel, Hashable):
    id: Snowflake
    name: str
    icon: str
    description: str
    summary: str
    bot: Optional[User]


class PartialIntegration(pydantic.BaseModel, Hashable):
    conn: Any

    id: Snowflake
    name: str
    type: str
    account: IntegrationAccount
    guild_id: Snowflake

    async def delete(self, *, reason: str = None) -> None:
        """|coro|

        Deletes integration

        Parameters
        ----------
        reason: :class:`str`
            Reason for deleting integration
        """
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.conn.request(
            Route("DELETE", path=f"/guilds/{self.guild_id}/integrations/{self.id}"),
            headers=headers
        )


class Integration(PartialIntegration):
    conn: Any

    enabled: bool
    syncing: Optional[bool]
    role_id: Optional[Snowflake]
    enable_emoticons: Optional[bool]
    expire_behavior: Optional[IntegrationExpBehaviour]
    expire_grace_period: Optional[int]
    user: Optional[User]
    synced_at: Optional[datetime.datetime]
    subscriber_count: Optional[int]
    revoked: Optional[bool]
    application: Optional[IntegrationApplication]
