from __future__ import annotations
from typing import Any, Optional
import pydantic

from acord.core.abc import Route
from acord.bases import Hashable
from acord.models import Snowflake, User
from acord.utils import _payload_dict_to_json


class Sticker(pydantic.BaseModel, Hashable):
    conn: Any

    id: Snowflake
    """ ID of the sticker """
    pack_id: Optional[Snowflake]
    """ for standard stickers, id of the pack the sticker is from """
    name: str
    """ name of the sticker """
    description: Optional[str]
    """ description of the sticker """
    tags: str
    """ autocomplete/suggestion tags for the sticker (max 200 characters) """
    asset: Optional[str]
    """ **DEPRECATED** previously the sticker asset hash, now an empty string """
    type: int
    """ type of sticker """
    format_type: int
    """ type of sticker format """
    available: Optional[bool]
    """ whether this guild sticker can be used, may be false due to loss of Server Boosts """
    guild_id: Optional[Snowflake]
    """ id of the guild that owns this sticker """
    user: Optional[User]
    """ the user that uploaded the guild sticker """
    sort_value: Optional[int]
    """ the standard sticker's sort order within its pack """

    @pydantic.validator("user")
    def _validate_user(cls, user, **kwargs):
        if not user:
            return
        conn = kwargs["values"]["conn"]
        user.conn = conn

        return user

    @classmethod
    async def from_code(cls, client, sticker_id: Snowflake) -> Sticker:
        """|coro|

        Fetches sticker from API,
        by using existing client and id

        Parameters
        ----------
        client: :class:`Client`
            client to fetch sticker from
        sticker_id: :class:`Snowflake`
            id of sticker to fetch
        """
        r = await client.http.request(Route("GET", path=f"/stickers/{sticker_id}"))
        return Sticker(**(await r.json()))

    async def delete(self, *, reason: str = None) -> None:
        """|coro|

        Deletes this sticker
        """
        headers = {}
        if reason is not None:
            headers["X-Audit-Log-Reason"] = reason

        await self.conn.request(
            Route("DELETE", path=f"/guilds/{self.guild_id}/stickers/{self.id}"),
            headers=headers,
        )

    async def edit(self, *, reason: str = None, **data) -> Sticker:
        """|coro|

        Modifies sticker

        Parameters
        ----------
        name: :class:`str`
            name of sticker
        description: :class:`str`
            description of sticker
        tags: :class:`str`
            tags for autocompletion of sticker
        """
        from acord.payloads import StickerEditPayload

        headers = {"Content-Type": "application/json"}

        if reason is not None:
            headers["X-Audit-Log-Reason"] = reason

        r = await self.conn.request(
            Route("PATCH", path=f"/guilds/{self.guild_id}/stickers/{self.id}"),
            headers=headers,
            data=_payload_dict_to_json(StickerEditPayload, **data),
        )

        return Sticker(conn=self.conn, **(await r.json()))
