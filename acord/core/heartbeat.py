# Basic heartbeat controller
from datetime import datetime
from threading import Thread
import asyncio
import time
from .signals import gateway  # type: ignore
import logging

logger = logging.getLogger(__name__)


class KeepAlive(Thread):
    def __init__(self, client, identity, ws, helloPacket: dict):
        self._client = client
        self._ws = ws
        self.packet = helloPacket
        self.identity = identity
        self.loop = asyncio.get_event_loop()

        super().__init__(daemon=True)

    def run(self):
        packet = self.packet

        asyncio.run_coroutine_threadsafe(self._ws.send_json(self.identity), self.loop)
        logger.info(f"Identity packet sent to gateway, starting heartbeats")

        while True:
            if packet["op"] != gateway.HELLO:
                raise ValueError("Invalid hello packet provided")

            coro = self._ws.send_json(self.get_payload())
            asyncio.run_coroutine_threadsafe(coro, self.loop)

            self._client.acked_at = time.perf_counter()
            logger.debug(
                f"Sending next heartbeat after {(packet['d']['heartbeat_interval'] / 1000)} seconds"
            )

            time.sleep((packet["d"]["heartbeat_interval"] / 1000))

        self.join()

    def get_payload(self):
        return {"op": gateway.HEARTBEAT, "d": self._client.sequence}


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
