from __future__ import annotations

from .base import Channel

from acord.models import Snowflake
from acord.bases import Hashable, StagePrivacyLevel, ChannelTypes
from acord.core.abc import Route
from acord.payloads import StageInstanceEditPayload
from acord.utils import _payload_dict_to_json
from typing import Any, Optional


class Stage(Channel, Hashable):
    conn: Any

    guild_id: Snowflake
    """ The guild id of the associated Stage channel """
    channel_id: Snowflake
    """ The id of the associated Stage channel """
    topic: str
    """ The topic of the Stage instance (1-120 characters) """
    privacy_level: StagePrivacyLevel
    """ The privacy level of the Stage instance """
    discoverable_disabled: bool
    """ Whether or not Stage Discovery is disabled """

    # Sometimes not provided so over ride with default type set
    type: Optional[ChannelTypes] = ChannelTypes.GUILD_STAGE_VOICE

    async def delete(self, *, reason: str = None) -> None:
        """|coro|

        Deletes this stage instance

        Parameters
        ----------
        reason: :class:`str`
            Reason for deleting instance        
        """
        headers = {}

        if reason is not None:
            headers["X-Audit-Log-Reason"] = reason

        await self.conn.request(
            Route("DELETE", path=f"/stage-instances/{self.channel_id}"),
            headers=headers
        )

    async def edit(self, *, reason: str = None, **data) -> Stage:
        """|coro|

        Edits this stage instance,
        returning updated instance

        Parameters
        ----------
        reason: :class:`str`
            reason for editing stage instance
        topic: :class:`str`
            new topic for stage instance
        privacy_level: :class:`StagePrivacyLevel`
            new privacy level for stage
        """
        headers = {"Content-Type": "application/json"}

        if reason is not None:
            headers["X-Audit-Log-Reason"] = reason

        r = await self.conn.request(
            Route("PATCH", path=f"/stage-instances/{self.channel_id}"),
            headers=headers,
            data=_payload_dict_to_json(StageInstanceEditPayload, **data)
        )

        return Stage(conn=self.conn, **(await r.json()))
