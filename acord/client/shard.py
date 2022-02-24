# Represents a shard
# Client will normally run off a single shard
from __future__ import annotations
import asyncio
from typing import Any
import logging
import pydantic

from acord.models import Snowflake

from .handler import handle_websocket
from acord.core.http import HTTPClient
from acord.core.signals import gateway
from acord.payloads import (
    GenericWebsocketPayload,
    VoiceStateUpdatePresence,
)
from acord.bases import Presence

logger = logging.getLogger(__name__)


class ShardingClient(HTTPClient):
    def getIdentityPacket(self, shard: tuple,
        intents=0, large_threshold=250, presence: dict = {}
    ):
        d = super().getIdentityPacket(intents, large_threshold, presence)
        d["d"]["shard"] = shard

        return d


class Shard(pydantic.BaseModel):
    """Representation of a discord shard

    Sharding is not enabled by default,
    if discord requires you to shard you may expect an error whilst starting the bot.

    .. note::
        You can enable sharding by using the ``sharding_enabled`` kwarg with the client class

    .. note::
        When providing a handler, 
        it must take care of reading the websocket,
        else see the implementation below.

    .. rubric:: Working with a shard

    .. code-block:: py

        shard = Shard

        # Connect
        await shard.connect()

        await shard.wait_until_ready()

        async for message in shard.ws:
            ...

    .. note::
        You can always use :meth:`Shard.listen` to do this for you,
        but make sure you have a handler attached.

    Parameters
    ----------
    shard_id: :class:`int`
        ID of shard
    handler: Callable[..., Coroutine[Any, Any, Any]]
        A handler to overwrite the default handler
    client: :class:`Client`
        Client this shard is attached to
    """

    shard_id: int
    handler: Any = handle_websocket
    client: Any     # type: acord.Client

    _ws: Any = None
    _ready_event = asyncio.Event()
    _http: Any = None
    _loop: Any = asyncio.get_event_loop()
    _task: Any = None

    def contains_guild(self, guild_id: Snowflake, /) -> bool:
        return ((guild_id >> 22) % self.client.MAX_CONC) == self.shard_id

    async def wait_until_ready(self):
        """|coro|

        Blocks until the shard is ready to receive messages
        """
        await self._ready_event.wait()

    async def connect(self, token: str, *, encoding, compress=0, **kwds) -> None:
        identity = kwds.pop("identity", {})

        if not self._http:
            self._http = ShardingClient(
                client=self.client, token=token,
                **kwds
            )

        identity.update({"shard": (self.shard_id, self.client.MAX_CONC)})

        ws = await self._http._connect(token=token, encoding=encoding, 
                                       compress=compress, **identity)
        self._ws = ws

        self._ready_event.set()

    async def disconnect(self):
        await self._http.disconnect()

        if self._task:
            self._task.cancel()

        self.client.shards.remove(self)

    async def listen(self, r_scripts, *args, **kwds) -> None:
        await self.connect(*args, **kwds)

        await handle_websocket(self.client, self.ws, r_scripts, ws_shard=self.shard_id)

    async def change_presence(self, presence: Presence) -> None:
        """|coro|

        Changes client presence

        Parameters
        ----------
        presence: :class:`Presence`
            New presence for client,
            You may want to checkout the guide for presences.
            Which can be found `here <../guides/presence.html>`_.
        """
        payload = GenericWebsocketPayload(op=gateway.PRESENCE, d=presence)

        logger.debug(f"Updating presence for shard {self.shard_id}")

        await self.ws.send_str(payload.json())

    async def update_voice_state(self, **data) -> None:
        """|coro|

        Updates client voice state

        Parameters
        ----------
        guild_id: :class:`Snowflake`
            id of the guild
        channel_id: :class:`Snowflake`
            id of the voice channel client wants to join (``None`` if disconnecting)
        self_mute: :class:`bool`
            is the client muted
        self_deaf: :class:`bool`
            is the client deafened
        """
        voice_payload = VoiceStateUpdatePresence(**data)
        payload = GenericWebsocketPayload(op=gateway.VOICE, d=voice_payload)

        await self.ws.send_str(payload.json())

    @property
    def ws(self):
        return self._ws

    @property
    def ratelimit_key(self):
        return self.shard_id % self.client.MAX_CONC
