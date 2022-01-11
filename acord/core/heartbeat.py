# Basic heartbeat controller
from threading import Thread
import asyncio
import time
from .signals import gateway  # type: ignore


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

        while True:
            if packet["op"] != gateway.HELLO:
                raise ValueError("Invalid hello packet provided")

            time.sleep((packet["d"]["heartbeat_interval"] / 1000))

            self.loop.create_task(self._ws.send_json(self.get_payload()))

        self.join()

    def get_payload(self):
        return {"op": gateway.HEARTBEAT, "d": gateway.SEQUENCE}


class VoiceKeepAlive(Thread):
    def __init__(self, ws, packet):
        self._ws = ws
        self.integer_nonce = 0
        self.packet = packet
        self.loop = asyncio.get_event_loop()

        super().__init__(daemon=True)

    def run(self):
        packet = self.packet

        while True:

            time.sleep((packet["d"]["heartbeat_interval"] / 1000))

            self.loop.create_task(self._ws.send_json(self.get_payload()))

        self.join()

    def get_payload(self):
        self.integer_nonce += 1
        return {"op": 3, "d": self.integer_nonce}
