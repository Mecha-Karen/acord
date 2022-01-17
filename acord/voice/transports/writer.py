from __future__ import annotations
from typing import Union

from io import BufferedIOBase
from os import PathLike

from acord.voice.core import VoiceWebsocket
from .base import BaseTransport


class BasePlayer(BaseTransport):
    def __init__(self, conn: VoiceWebsocket, data: Union[BufferedIOBase, PathLike]) -> None:
        if not isinstance(data, BufferedIOBase):
            self.fp = open(data, "rb")
            self.pos = 0
        else:
            self.fp = data
            self.pos = data.tell()

        self.packet_limit = 2 ** 16 # 64 kB
        self.index = 0

        self.closed = False
        super().__init__(conn)

    def __aiter__(self):
        return self

    async def __anext__(self):
        self.index += 1
        data = self.fp.read((self.packet_limit * self.index))
        if not data:
            self.close()
            raise StopAsyncIteration
        self.pos = self.fp.read()
        return data

    async def close(self) -> None:
        if self.closed:
            raise ValueError("Transport already closed")

        self.fp.close()
        self.closed = True

    async def cleanup(self) -> None:
        ...

    async def send(self, data: bytes, *, flags: int = 0) -> None:
        await self.conn.send_audio_packet(
            data, has_header=False, sock_flags=flags
        )

    async def play(self, *, flags: int = 0) -> None:
        async for packet in self:
            await self.send(data=packet, flags=flags)
