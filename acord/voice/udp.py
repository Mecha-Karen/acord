from __future__ import annotations

from asyncio.events import AbstractEventLoop
import socket
import logging

logger = logging.getLogger(__name__)


class SocketWrapper(socket.socket):
    def __init__(self, loop: AbstractEventLoop, **kwds):
        self.loop = loop

        super().__init__(**kwds)

    async def connect(self, addr: tuple) -> None:
        await self.loop.run_in_executor(
            None, super().connect, addr
        )

    async def close(self) -> None:
        await self.loop.run_in_executor(
            None, super().close
        )

    async def read(self, limit: int, flags: int = -1) -> bytes:
        return await self.loop.run_in_executor(
            None, super().recv, limit, flags
        )

    async def write(self, data: bytes, flags: int = -1) -> None:
        await self.loop.run_in_executor(
            None, super().send, data, flags 
        )


class UDPConnection(object):
    def __init__(self, 
        host, port, loop,
        client, vc_Ws, conn_id,
        **kwds
    ) -> None:
        kwds.update({"type": socket.AF_INET, "family": socket.SOCK_DGRAM})

        self.host = host
        self.port = port
        self.loop = loop
        self.client = client
        self.ws = vc_Ws
        self.conn_id = conn_id

        self.sock_kwds = kwds
        self.limit = 2 ** 16

        self._sock = None

    async def connect(self) -> None:
        # Creates a UDP connection between host and port
        sock = SocketWrapper(self.loop, **self.sock_kwds)

        connected = False

        for i in range(5):
            try:
                logger.debug(f"Attempting to connect to {self.host}:{self.port}, attempt {i}")
                await sock.connect((self.host, self.port))

                connected = True
                break
            except Exception as exc:
                if exc.args and exc.args[0] in (121, 10060):
                    logger.warn(f"Failed to connect to {self.host}:{self.port}, retrying ...")
                    continue
                raise

        if not connected:
            logger.error(f"Failed to connect to {self.host}:{self.port} after 5 attempts")
            raise ConnectionRefusedError(f"Unable to connect to UDP endpoint after {i} attempts,\
                 conn_id={self.conn_id}")

        self._sock = sock

    async def close(self) -> None:
        await self._sock.close()

    async def read(self, *, limit: int = None, flags: int = -1) -> bytes:
        limit = limit or self.limit
        return await self._sock.read(limit, flags)

    async def write(self, data: bytes, *, flags: int = -1) -> None:
        return await self._sock.write(data, flags)
