from __future__ import annotations
from typing import Iterator, Optional

from .base import BaseTransport


class BaseReciever(BaseTransport):
    def __init__(self, conn, *, limit: int = None, flags: int = 0) -> None:
        super().__init__(conn)

        self.last_packet: bytes = None
        self.last_packet_empty: bool = None

        self.limit = limit
        self.flags = flags
        self.is_closed = False

        self._task = self.sock.loop.create_task(self.dispatcher(limit=limit, flags=flags))

    def __aiter__(self) -> Iterator[Optional[bytes]]:
        return self

    async def __anext__(self):
        if self.is_closed:
            raise StopAsyncIteration

        try:
            return await self.recieve(limit=self.limit, flags=self.flags)
        except OSError:
            self.is_closed = True
            raise StopAsyncIteration

    async def recieve(self, 
        *, 
        limit: int = None, 
        flags: int = -1, 
        decode: bool = False
    ) -> Optional[bytes]:
        if decode:
            raise NotImplementedError("Decoding voice data has not been implemented yet")
        if self.is_closed:
            raise ValueError("Transport is closed")

        return await self.sock.read(limit=limit, flags=flags)

    async def close(self, *, cleanup: bool = False) -> None:
        res = self._task.cancel("Transport closed")

        if not res:
            raise RuntimeError("Failed to stop task whilst closing transport")

        if cleanup:
            await self.cleanup()
        self.is_closed = True

    async def cleanup(self) -> None:
        self.last_packet = None
        self.last_packet_empty = None

    async def dispatcher(self, *, limit: int = None, flags: int = None) -> None:
        await self.sock.wait_until_connected()

        while True:
            data = await self.recieve(limit=limit, flags=flags)
            self.last_packet = data
            self.last_packet_empty = bool(len(data))

            self.conn._client.dispatch("voice_data_recv", data)
