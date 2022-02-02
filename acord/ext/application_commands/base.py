from __future__ import annotations
from typing import Any, List, Optional

import pydantic
from acord.models import (
    Snowflake,
)
from acord.core.abc import Route
from acord.utils import _payload_dict_to_json
from acord.bases import Hashable
from .types import ApplicationCommandType
from .option import SlashOption


class UDAppCommand(pydantic.BaseModel, Hashable):
    """Identifier for all user defined slash commands,
    e.g. classes such as SlashBase.
    """
    __slots__ = ()


class ApplicationCommand(pydantic.BaseModel):
    conn: Any

    application_id: Snowflake
    """ unique id of the parent application """
    id: Snowflake
    """ Unique ID of the command """
    name: str
    """ Name of command """
    description: str
    """ Description of the command, 
    empty strings when type != :attr:`ApplicationCommandType.CHAT_INPUT` """
    version: str
    """autoincrementing version identifier updated during substantial record changes"""
    type: Optional[ApplicationCommandType] = ApplicationCommandType(1)
    """ the type of command, defaults ``1`` if not set """
    guild_id: Optional[Snowflake]
    """ guild id of the command, if not global """
    default_permission: Optional[bool] = True
    """ whether the command is enabled by default when the app is added to a guild """
    options: Optional[List[SlashOption]] = []
    """ Options for a slash command """

    async def delete(self) -> None:
        """|coro|

        Deletes this command globally,
        if ``guild_id`` is not ``None``,
        the command is deleted for that guild
        """
        if self.guild_id is not None:
            path = f"/applications/{self.application_id}/guilds/{self.guild_id}/commands/{self.id}"
        else:
            path = f"/applications/{self.application_id}/commands/{self.id}"

        await self.conn.request(
            Route("DELETE", path=path, bucket=dict(guild_id=self.guild_id))
        )

    async def edit(self, **data) -> ApplicationCommand:
        """|coro|

        Edits this command globally,
        if ``guild_id`` is not ``None``,
        the command is edited just for that guild

        Parameters
        ----------
        """
        from acord.payloads import ApplicationCommandEditPayload

        if self.guild_id is not None:
            path = f"/applications/{self.application_id}/guilds/{self.guild_id}/commands/{self.id}"
        else:
            path = f"/applications/{self.application_id}/commands/{self.id}"

        m = _payload_dict_to_json(ApplicationCommandEditPayload, **data)

        r = await self.conn.request(
            Route("PATCH", path=path, data=m)
        )

        return ApplicationCommand(conn=self.conn, **(await r.json()))
