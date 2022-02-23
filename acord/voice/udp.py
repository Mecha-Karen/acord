from __future__ import annotations
import asyncio

from asyncio.events import AbstractEventLoop
import socket
import logging

logger = logging.getLogger(__name__)


class SocketWrapper(socket.socket):
    def __init__(self, loop: AbstractEventLoop, **kwds):
        self.loop = loop

        super().__init__(**kwds)

    async def connect(self, addr: tuple) -> None:
        await self.loop.run_in_executor(None, super().connect, addr)

    async def close(self) -> None:
        await self.loop.run_in_executor(None, super().close)

    async def read(self, limit: int, flags: int = 0) -> bytes:
        return await self.loop.run_in_executor(None, super().recv, limit, flags)

    async def write(self, data: bytes, flags: int = 0) -> None:
        await self.loop.run_in_executor(None, super().send, data, flags)

    async def sendto(self, data, addr) -> None:
        await self.loop.run_in_executor(None, super().sendto, data, addr)


class UDPConnection(object):
    """Represents a UDP connection

    Attributes
    ----------
    host: :class:`str`
        IP of host
    port: :class:`int`
        Port connected to
    loop: :obj:`py:asyncio.AbstractLoopEvent`
        Loop that is being used
    vc_Ws: :class:`VoiceConnection`
        Voice Connection using this UDP connection
    conn_id: :class:`int`
        The conn_id assigned to the voice connection
    **kwds:
        Any kwargs for connecting to the socket,
        type and family are overwritten.
    """
    def __init__(self, host, port, loop, client, vc_Ws, conn_id, **kwds) -> None:
        kwds.update({"type": socket.AF_INET, "family": socket.SOCK_DGRAM})

        self.host = host
        self.port = port
        self.loop = loop
        self.client = client
        self.ws = vc_Ws
        self.conn_id = conn_id

        self.sock_kwds = kwds
        self.limit = 10240

        self._sock = None
        self._sock_event = asyncio.Event()

    async def connect(self) -> None:
        """|coro|

        Connects to the UDP port.
        
        .. note::
            It will attempt to connect to the port 5 times before failing,
            this will only occur when it fails with codes 121 or 10060.
        """
        sock = SocketWrapper(self.loop, **self.sock_kwds)

        connected = False

        for i in range(5):
            try:
                logger.debug(
                    f"Attempting to connect to {self.host}:{self.port}, attempt {i}"
                )
                await sock.connect((self.host, self.port))

                connected = True
                break
            except Exception as exc:
                if exc.args and exc.args[0] in (121, 10060):
                    logger.warn(
                        f"Failed to connect to {self.host}:{self.port}, retrying ..."
                    )
                    continue
                raise

        if not connected:
            logger.error(
                f"Failed to connect to {self.host}:{self.port} after 5 attempts"
            )
            raise ConnectionRefusedError(
                f"Unable to connect to endpoint after {i} attempts,\
                 conn_id={self.conn_id}"
            )

        self._sock = sock
        self._sock_event.set()

    def is_connected(self):
        """ Whether the socket is connected """
        return self._sock_event.is_set()

    async def wait_until_connected(self) -> None:
        """|coro|
        
        Wait until the socket has connected """
        await self._sock_event.wait()

    async def close(self) -> None:
        """|coro|

        Closes the socket connection """
        logger.debug(f"Closing connection with {self.host}:{self.port}")
        await self._sock.close()

    async def read(self, *, limit: int = None, flags: int = 0) -> bytes:
        """|coro|
        
        Reads from the socket stream

        Parameters
        ----------
        limit: :class:`int`
            How many bytes to read
        flags: :class:`int`
            Any sock flags
        """
        limit = limit or self.limit

        logger.debug(f"Reading {limit} bytes from {self._sock}")
        return await self._sock.read(limit, flags)

    async def write(self, data: bytes, *, flags: int = 0) -> None:
        """|coro|

        Writes to the socket stream

        Parameters
        ----------
        data: :class:`bytes`
            Bytes to write to stream
        flags: :class:`int`
            Any sock flags
        """
        logger.debug(f"Sending {len(data)} bytes to {self.host}:{self.port}")
        return await self._sock.write(data, flags)

    async def sendto(self, data: bytes, addr: tuple) -> None:
        """|coro|

        Choose to send bytes directly to the provided addr

        Parameters
        ----------
        data: :class:`bytes`
            Bytes to send
        addr: :class:`tuple`
            A tuple containing the address and port
        """
        logger.debug(f"Send to being called, addr={addr}")
        return await self._sock.sendto(data, addr)
