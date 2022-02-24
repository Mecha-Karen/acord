# Represents a shard
# Client will normally run off a single shard
from __future__ import annotations
import asyncio
import sys
from typing import Any, Callable, Coroutine, Union
from aiohttp import ClientSession
import logging
from acord.core.heartbeat import KeepAlive
from acord.errors import GatewayError

from acord.models import Snowflake

from .handler import handle_websocket
from acord.core.signals import gateway
from acord.payloads import (
    GenericWebsocketPayload,
    VoiceStateUpdatePresence,
)
from acord.bases import Presence

logger = logging.getLogger(__name__)


IDENTITY_PCK = {
    "properties": {
        "$os": sys.platform,
        "$browser": "acord",
        "$device": "acord",
        "$referrer": None,
        "$referring_domain": None,
    },
    "compress": True,
    "large_threshold": 250,
}


class Shard:
    """Representation of a discord shard,
    which is basically a connection to the gateway.

    .. warning::
        Shards are enabled by default but only Shard 0 will receive dms

    .. note::
        When providing a handler, 
        it must take care of reading the websocket,
        else see the implementation below.

    .. rubric:: Working with a shard

    .. code-block:: py

        shard = Shard("url", shard_id, num_shards, client)

        # Connect
        await shard.connect()

        await shard.wait_until_ready()

        async for message in shard.ws:
            ...

    .. note::
        You can always use :meth:`Shard.listen` to do this for you.

    Parameters
    ----------
    shard_id: :class:`int`
        ID of shard
    handler: Callable[..., Coroutine[Any, Any, Any]]
        A handler to overwrite the default handler
    client: :class:`Client`
        Client this shard is attached to.
    """
    def __init__(self,
        url: str,
        shard_id: int,
        num_shards: int,
        client: Any,
        handler: Callable[..., Coroutine[Any, Any, Any]] = handle_websocket
    ):
        self.url = url
        self.shard_id = shard_id
        self.num_shards = num_shards
        self.client = client
        self.session = client.http._session
        self.handler = handler

        self.ws = None
        self.ready_event = asyncio.Event()
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        self.sequence = None
        self.session_id = None
        self.gateway_version = None
        self.resuming = False

    def contains_guild(self, guild_id: Snowflake, /) -> bool:
        return ((guild_id >> 22) % self.num_shards) == self.shard_id

    async def wait_until_ready(self):
        """|coro|

        Blocks until the shard is ready
        """
        await self._ready_event.wait()

    async def connect(self, **kwds) -> None:
        """|coro|

        Connects to gateway

        Parameters
        ----------
        token: :class:`str`
            Token to be used for identity packet
        **kwds:
            Additional kwargs to be passed through ``ws_connect`` 
        """
        logger.debug(f"Attempting to create a connection for shard {self.shard_id}")

        self.ws = await self.session.ws_connect(self.url, **kwds)
        self._snd_kwds = kwds

        logger.info(f"Shard {self.shard_id} has connected sucessfully")

    async def receive_hello(self):
        """|coro|

        Receives the hello packet from discord and begins heartbeating,
        should be called directly after :meth:`Shard.connect`
        """
        logger.debug(f"Receiving hello packet for Shard {self.shard_id}")

        packet = await self.ws.receive()
        data = packet.json()

        if not data["op"] == gateway.HELLO:
            raise GatewayError(f"Invalid op code recieved, got {packet['op']} expected {10}")

        self._keep_alive = KeepAlive(
            self, data["d"]["heartbeat_interval"], self.loop
        )
        self._keep_alive.start()

        logger.info(f"Hello packet sucessfully received, beginning heartbeats for Shard {self.shard_id}")

    async def send_identity(self, token: str, intents: int, presence: Presence = None) -> None:
        """|coro|

        Sends an identity packet to discord

        Parameters
        ----------
        token: :class:`str`
            Bot token
        intents: :class:`int`
            Intents to send
        presence: :class:`Presence`
            An optional presence to update the client with
        """
        idn = IDENTITY_PCK.copy()
        idn.update({
            "token": token,
            "intents": intents,
            "presence": presence,
            "shard": (self.shard_id, self.num_shards)
        })

        payload = GenericWebsocketPayload(
            op=gateway.IDENTIFY,
            d=idn
        )

        await self.ws.send_str(payload.json())

        logger.info(f"Sent identity packet for Shard {self.shard_id}")

    async def listen(self, **kwds):
        """Generates task using handler,
        this task is automatically terminated by :meth:`Shard.disconnect`.

        .. note::
            Any kwargs you pass through are sent to the handler
        """
        coro = self.handler(self, **kwds)

        # task = self.loop.create_task(coro, name=f"ShardHandler:shard_id={self.shard_id}")
        # self.task = task
        await coro

    async def disconnect(self):
        logger.info(f"Disconnecting from shard {self.shard_id}")

        if self.task:
            self.task.cancel(msg="Shard disconnected")

        self._keep_alive._ended = True

        await self.ws.close(code=4000)

        self.client.shards.remove(self)

    async def resume(self, *, restart: bool = False):
        """|coro|

        Sends a resume packet to discord

        Parameters
        ----------
        restart: :class:`bool`
            Whether to restart the session
        """
        if restart:
            await self.ws.close(code=4000)
            await self.connect(**self._snd_kwds)

        self.resuming = True

        await self.ws.send_json({
            "op": gateway.RESUME,
            "d": {
                "token": self.client.token,
                "session_id": self.session_id,
                "seq": self.sequence
            }
        })

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
    def ratelimit_key(self):
        return self.shard_id % self.session.MAX_CONC

    def __repr__(self):
        return f"Shard(id={self.id}, running={self.ws is not None})"
