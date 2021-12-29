from typing import Any, Optional
import pydantic
from acord.bases.flags.channels import ChannelTypes

from acord.core.abc import Route
from acord.bases import Hashable
from acord.errors import Forbidden


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
            # TODO: Guild object
            if any(
                [
                    self.guild.rule_channels == self,
                    self.guild.guidelines_channel == self,
                    self.guild.community_updates_channel == self,
                ]
            ):
                raise Forbidden(
                    "For Community guilds, the Rules or Guidelines channel and the Community Updates channel cannot be deleted."
                )

        await self.conn.request(
            Route("DELETE", path=f"/channels/{self.id}"),
            headers={"X-Audit-Log-Reason": reason},
        )
