# Basic heartbeat controller
from datetime import datetime
from threading import Thread
import asyncio
import time
from .signals import gateway  # type: ignore
import logging

logger = logging.getLogger(__name__)


class KeepAlive(Thread):
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

        logger.info(f"Sent heartbeat for shard {self.shard.shard_id}, waiting {self._interval} seconds...")

    def get_payload(self):
        return {"op": gateway.HEARTBEAT, "d": self.shard.sequence}

    def ack(self):
        d = time.perf_counter()
        self._waiting_for_ack = False

        self.latency = d - self.sent_at


class VoiceKeepAlive(Thread):
    def __init__(self, cls, packet):
        self.integer_nonce = 0
        self.packet = packet
        self.loop = asyncio.get_event_loop()
        self.cls = cls

        self.ended = False

        super().__init__(daemon=True)

    def end(self):
        self.ended = True

    def run(self):
        packet = self.packet

        while not self.ended:

            time.sleep((packet["d"]["heartbeat_interval"] / 1000))

            try:
                while not self.cls._ws:
                    pass

                self.loop.create_task(self.cls._ws.send_json(self.get_payload()))
                self.cls.acked_at = datetime.utcnow().timestamp()
                logger.debug(f"Sent heartbeat for voice channel, ended: {self.ended}")
            except ConnectionResetError:
                logger.warn("Connection reset for voice heartbeat, ending heartbeat")
                self.ended = True
                self.join()

    def get_payload(self):
        self.integer_nonce += 1
        return {"op": 3, "d": self.integer_nonce}
