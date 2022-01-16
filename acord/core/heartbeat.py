# Basic heartbeat controller
from threading import Thread
import asyncio
import time
from .signals import gateway  # type: ignore
import logging

logger = logging.getLogger(__name__)


class KeepAlive(Thread):
    def __init__(self, identity, ws, helloPacket: dict):
        self._ws = ws
        self.packet = helloPacket
        self.identity = identity
        self.loop = asyncio.get_event_loop()

        super().__init__(daemon=True)

    def run(self):
        packet = self.packet

        self.loop.create_task(self._ws.send_json(self.identity))
        logger.info(f"Identity packet sent, contents:\n{self.identity}")

        while True:
            if packet["op"] != gateway.HELLO:
                raise ValueError("Invalid hello packet provided")

            logger.debug("Sending new heartbeat, waiting...")
            time.sleep((packet["d"]["heartbeat_interval"] / 1000))

            self.loop.create_task(self._ws.send_json(self.get_payload()))
            logger.debug(f"Sent heartbeat after {(packet['d']['heartbeat_interval'] / 1000)} seconds")

        self.join()

    def get_payload(self):
        return {"op": gateway.HEARTBEAT, "d": gateway.SEQUENCE}


class VoiceKeepAlive(Thread):
    def __init__(self, cls, packet):
        self.integer_nonce = 0
        self.packet = packet
        self.loop = asyncio.get_event_loop()
        self.cls = cls

        self.ended = False

        super().__init__(daemon=True)

    def run(self):
        packet = self.packet

        while not self.ended:

            time.sleep((packet["d"]["heartbeat_interval"] / 1000))

            try:
                while not self.cls._ws:
                    continue

                self.loop.create_task(self.cls._ws.send_json(self.get_payload()))
                logger.debug("Sent heartbeat for voice channel")
            except ConnectionResetError:
                logger.warn("Connection reset for voice heartbeat, ending heartbeat")
                self.ended = True

    def get_payload(self):
        self.integer_nonce += 1
        return {"op": 3, "d": self.integer_nonce}
