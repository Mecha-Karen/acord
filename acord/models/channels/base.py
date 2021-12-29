from typing import Any, Optional
import pydantic
from acord.bases.flags.channels import ChannelTypes

from acord.core.abc import Route
from acord.bases import Hashable
from acord.errors import Forbidden
from acord.models.guild import Guild


# All channel objects will inherit this class
class Channel(pydantic.BaseModel, Hashable):
    conn: Any  # Connection object - Internal use only

    id: int  # Channel ID
    type: ChannelTypes  # Channel type, e.g 0 -> GUILD_TEXT

    async def delete(self, *, reason: str) -> None:
        # Only applies for guilds:
        # If the channel is of a specific type, instead of making an extra call
        # Raise forbidden directly
        if getattr(self, "guild") and "COMMUNITY" in self.guild.features:
            if any(
                [
                    self.guild.rules_channel_id == self.id,
                    self.guild.system_channel_id == self.id,
                    self.guild.public_updates_channel_id == self,
                ]
            ):
                raise Forbidden(
                    "For Community guilds, the Rules or Guidelines channel and the Community Updates channel cannot be deleted."
                )

        await self.conn.request(
            Route("DELETE", path=f"/channels/{self.id}"),
            headers={"X-Audit-Log-Reason": reason},
        )
