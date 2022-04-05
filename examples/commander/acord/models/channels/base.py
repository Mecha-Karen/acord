from typing import Any
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
        await self.conn.request(
            Route("DELETE", path=f"/channels/{self.id}"),
            headers={"X-Audit-Log-Reason": reason},
        )
