# Basic heartbeat controller
from abc import ABC, abstractmethod
from threading import Thread
import asyncio
import time
from .signals import gateway  # type: ignore
import logging

logger = logging.getLogger(__name__)


class KeepAlive(Thread, ABC):
    """Represents a keep alive handler.

    .. DANGER::
        If you are not overwriting :meth:`KeepAlive.run`,
        you will need to provide the following attrs.

    Attributes
    ----------
    _ended: :class:`bool`
        Whether heartbeating has ended
    _interval: :class:`int`
        Time to wait between heartbeats,
        in seconds.
    """

    _ended: bool
    _interval: int

    def run(self):
        """Default .run function,
        calls :meth:`KeepAlive.send_heartbeat` every n seconds.

        .. note::
            Once ended,
            ``.join`` is called within this function
        """
        while not self._ended:
            self.send_heartbeat()

            time.sleep(self._interval)

        self.join()

    @abstractmethod
    def send_heartbeat(self):
        """Sends a heartbeat"""

    @abstractmethod
    def get_payload(self):
        """Gets heartbeat payload"""

    @abstractmethod
    def ack(self):
        """Called when server responds with an ACK to our heartbeat"""


class GatewayKeepAlive(KeepAlive):
    def __init__(self, shard, interval, loop=asyncio.get_event_loop()):
        self.sent_at = None
        self.latency = float("inf")
        self.shard = shard

        self._loop: asyncio.AbstractEventLoop = loop
        self._ws = shard.ws
        self._interval = interval / 1000

        self._ended = False
        self._waiting_for_ack = False

        super().__init__(daemon=True)

    def run(self):
        while not self._ended:
            self.send_heartbeat()

            time.sleep(self._interval)

        self.join()

    def send_heartbeat(self):
        coro = self._ws.send_json(self.get_payload())
        asyncio.run_coroutine_threadsafe(coro, self._loop)

        self.sent_at = time.perf_counter()
        self._waiting_for_ack = True

        logger.info(
            f"Sent heartbeat for shard {self.shard.shard_id}, waiting {self._interval} seconds..."
        )

    def get_payload(self):
        return {"op": gateway.HEARTBEAT, "d": self.shard.sequence}

    def ack(self):
        d = time.perf_counter()
        self._waiting_for_ack = False

        self.latency = d - self.sent_at


class VoiceKeepAlive(KeepAlive):
    def __init__(self, connection, packet, loop=asyncio.get_event_loop()) -> None:
        self.integer_nonce = 0
        self.sent_at = None
        self.latency = float("inf")
        self.connection = connection

        self._loop = loop
        self._interval = packet["d"]["heartbeat_interval"] / 1000
        self._ended = False
        self._ws = connection._ws

    def send_heartbeat(self):
        coro = self._ws.send_json(self.get_payload())
        asyncio.run_coroutine_threadsafe(coro, self._loop)

        self.sent_at = time.perf_counter()
        self._waiting_for_ack = True

        logger.info(f"Sent Heartbeat to voice channel, conn_id={self.connection}")

    def ack(self):
        d = time.perf_counter()
        self._waiting_for_ack = False

        self.latency = d - self.sent_at

    def get_payload(self):
        self.integer_nonce += 1
        return {"op": 3, "d": self.integer_nonce}

    def end(self):
        self._ended = True
