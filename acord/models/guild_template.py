from __future__ import annotations

import pydantic

from typing import Any, Optional
from acord.core.abc import Route
from acord.models import Snowflake, User
from acord.payloads import TemplateCreatePayload


class GuildTemplate(pydantic.BaseModel):
    conn: Any

    code: str
    """ the template code (unique ID) """
    name: str
    """ template name """
    description: Optional[str]
    """ the description for the template """
    usage_count: int
    """ number of times this template has been used """
    creator_id: Snowflake
    """ the ID of the user who created the template """
    creator: User
    """ the user who created the template """
    created_at: str
    """ when this template was created """
    updated_at: str
    """ when this template was last synced to the source guild """
    source_guild_id: Snowflake
    """ the ID of the guild this template is based on """
    serialized_source_guild: Any
    """ the guild snapshot this template contains """
    is_dirty: Optional[bool]
    """ whether the template has unsynced changes """

    @pydantic.validator("creator")
    def _validate_conns(cls, **kwargs):
        conn = kwargs["values"]["conn"]

        creator = kwargs["values"]["creator"]
        creator.conn = conn

        return creator

    @pydantic.validator("serialized_source_guild", pre=True)
    def _get_cached_guild(cls, _, **kwargs) -> Any:
        conn = kwargs["values"]["conn"]
        id = kwargs["values"]["source_guild_id"]

        return conn.client.get_guild(id)

    async def sync(self) -> GuildTemplate:
        """|coro|

        Syncs current guild template.
        """
        r = await self.conn.request(
            Route("PUT", path=f"/guilds/{self.id}/templates/{self.code}")
        )

        return GuildTemplate(conn=self.conn, **(await r.json()))

    async def edit(self, **data) -> GuildTemplate:
        """|coro|

        Edits current template

        Parameters
        ----------
        name: :class:`str`
            name of template
        description: :class:`str`
            description of template
        """
        payload = TemplateCreatePayload(**data)

        r = await self.conn.request(
            Route("PATCH", path=f"/guilds/{self.id}/templates/{self.code}"),
            data=payload.json(),
            headers={"Content-Type": "application/json"}
        )

        return GuildTemplate(conn=self.conn, **(await r.json()))

    async def delete(self) -> GuildTemplate:
        """|coro|

        Deletes template, returns template on success.
        """
        r = await self.conn.request(
            Route("DELETE", path=f"/guilds/{self.id}/templates/{self.code}")
        )

        return GuildTemplate(**(await r.json()))
