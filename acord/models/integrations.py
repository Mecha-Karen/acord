from __future__ import annotations
from typing import Any, Optional
from enum import IntEnum
import pydantic
import datetime

from acord.models import User, Snowflake
from acord.core.abc import Route


class IntegrationExpBehaviour(IntEnum):
    REMOVE_ROLE = 0
    KICK = 1


class IntegrationAccount(pydantic.BaseModel):
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
    conn: Any

    id: Snowflake
    guild_id: Snowflake
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
