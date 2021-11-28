from __future__ import annotations

from typing import Any, List, Literal, Optional, Union
import datetime

import pydantic

from acord.bases.flags.channels import ChannelTypes
from acord.core.abc import DISCORD_EPOCH, Route
from acord.models import Message

from .__main__ import Channel


# Standard text channel in a guild
class TextChannel(Channel):
    guild_id: int  # ID of guild which it belongs to
    position: int  # Position of channel
    permission_overwrites: List[Any]  # Permissions of channel
    name: str  # Name of channel
    topic: Optional[str]  # Channel topic
    nsfw: Optional[bool]  # Channel is marked as NSFW
    last_message_id: Optional[int]  # Last message in channel, may or may not be valid
    parent_id: Optional[int]  # Category to which the channel belongs to
    last_pin_timestamp: Optional[int]  # Last pinned message in channel, may be None
    permissions: Optional[str]  # String of user permissions
    rate_limit_per_user: Optional[int]  # Channel ratelimit
    default_auto_archive_duration: Optional[
        int
    ]  # Default time for threads to be archived

    created_at: Optional[datetime.datetime]

    @pydantic.validator("created_at")
    def _validate_snowflake(cls, _, **kwargs) -> Optional[datetime.datetime]:
        if _:
            raise ValueError("Time provided, not able to parse")

        timestamp = ((kwargs["values"]["id"] >> 22) + DISCORD_EPOCH) / 1000

        return datetime.datetime.fromtimestamp(timestamp)

    @pydantic.validate_arguments
    async def edit(
        self,
        *,
        name: Optional[str] = None,
        type: Optional[Literal[0, 5]] = None,
        position: Optional[int] = None,
        topic: Optional[str] = None,
        nsfw: Optional[bool] = None,
        ratelimit: Optional[int] = None,
        permission_overwrites: Optional[List[Any]] = None,
        category: Optional[int] = None,
        archive_duration: Optional[Literal[0, 60, 1440, 4230, 10080]] = None,
        reason: Optional[str] = None,
    ):
        """
        Modifies a guild channel, fires a ``channel_update`` event if channel is updated.

        Parameters
        ----------
        name: :class:`str`
            New name for the channel
        type: Literal[0, 5]
            Change the type for the channel, currently on GUILD_TEXT and GUILD_NEWS is supported
        position: :class:`int`
            Change the position of the channel
        topic: :class:`str`
            Change the channels topic, if you wish to remove it use the :class:`MISSING` class
        nsfw: :class:`bool`
            Whether to mark channel as NSFW
        ratelimit: :class:`int`
            Change ratelimit value for channel
        permission_overwrite: List[Any]
            Currently not available
        category: Union[:class:`int`, CategoryChannel]
            Move the channel to a different category, use :class:`MISSING` for no category
        archive_duration: :class:`int`
            Change the default archive duration on a thread, use :class:`MISSING` or 0 for no timeout
        """
        payload = {
            "name": (name or self.name),
            "type": ((type if type is not None else None) or self.type),
            "position": (position or self.position),
            "topic": (topic or self.topic),
            "nsfw": ((nsfw if nsfw is not None else None) or self.nsfw),
            "rate_limit_per_user": (
                (ratelimit if ratelimit is not None else None)
                or self.rate_limit_per_user
            ),
            "permissions_overwrites": (
                permission_overwrites or self.permission_overwrites
            ),
            "parent_id": (getattr(category, "id", category) or None),
            "default_auto_archive_duration": (
                (archive_duration if archive_duration is not None else archive_duration)
                or self.default_auto_archive_duration
            ),
        }
        bucket = dict(channel_id=self.id, guild_id=self.guild_id)

        if permission_overwrites:
            raise NotImplemented

        # Rest should be standard python vars

        await self.conn.request(
            Route("PATCH", path=f"/channels/{self.id}", bucket=bucket),
            data=payload,
            headers={"X-Audit-Log-Reason": reason},
        )

    @pydantic.validate_arguments
    async def fetch_messages(
        self,
        *,
        around: Optional[Union[Message, int]] = None,
        before: Optional[Union[Message, int]] = None,
        after: Optional[Union[Message, int]] = None,
        limit: Optional[int] = 50,
    ) -> List[Message]:
        bucket = dict(channel_id=self.id, guild_id=self.guild_id)

        around = getattr(around, 'id', around)
        before = getattr(before, 'id', before)
        after = getattr(after, 'id', after)

        if 0 < limit < 100:
            raise ValueError('Messages to fetch must be an interger between 0 and 100')

        data = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/messages", bucket=bucket),
            data={"around": around, "before": before, "after": after, "limit": limit},
        )

        print(data)
