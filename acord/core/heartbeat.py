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

        super().__init__()

    def run(self):
        packet = self.packet

        self.loop.create_task(self._ws.send_json(self.identity))

        while True:
            if packet["op"] != gateway.HELLO:
                raise ValueError("Invalid hello packet provided")

            time.sleep((packet["d"]["heartbeat_interval"] / 1000))

            self.loop.create_task(self._ws.send_json(self.get_payload()))

    def get_payload(self):
        return {"op": gateway.HEARTBEAT, "d": gateway.SEQUENCE}
