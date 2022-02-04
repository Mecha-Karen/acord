from __future__ import annotations
import abc
from typing import Optional

try:
    from ..core import VoiceConnection
except ImportError:
    VoiceConnection = None


class BaseTransport(abc.ABC):
    """Base transport for working with the UDP connection

    Parameters
    ----------
    conn: :class:`VoiceConnection`
        Original websocket class when starting voice connection
    sock: :class:`UDPConnection`
        UDP socket class
    """

    # recieve and send are not abstract methods as 1 needs to be overwritten for a given transport

    __slots__ = ("conn", "sock")

    def __init__(self, conn: VoiceConnection) -> None:
        self.conn = conn
        self.sock = conn._sock

    async def recieve(
        self,
        *,
        limit: int = None,
        flags: int = -1,
        decode: bool = False,
    ) -> Optional[bytes]:
        """|coro|

        Reads data from stream,
        recievers will automatically read and dispatch data from streams.
        Writers should not implement this method but if needed try implement a reciever

        Parameters
        ----------
        limit: :class:`int`
            How much data to read,
            defaults to 64Kb
        flags: :class:`int`
            Additional flags to be used when reading stream
        decode: :class:`bool`
            Whether to decode data recieved from discord,
            defaults to ``False``
        """
        raise NotImplementedError

    async def send(
        self, data: bytes, *, flags: int = 0, c_flags: int = 5, continued: bool = False
    ) -> None:
        """|coro|

        Sends data through stream,
        writers must include this method and should make sure each packet has an RTC header.
        To simplify this mess you should call :class:`VoiceConnection._get_audio_packet`.

        .. note::
            When implementing writers,
            big files should be handled by you and for sending "complete" payloads,
            call :class:`VoiceConnection.send_audio_packet`.

        Parameters
        ----------
        data: :class:`bytes`
            data to send
        flags: :class:`int`
            additional flags when sending data,
            for UDP socket NOT websocket!
        c_flags: :class:`int`
            Flags for client when speaking,
            defaults to 5, requesting priority and microphone.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def close(self) -> None:
        """|coro|

        Closes this transport,
        leaving UDP connection open!

        For recievers this should be set to stop recieving,
        and for writers to close any files + stop writing.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def cleanup(self) -> None:
        """|coro|

        Cleans up any cache, if any.
        Should be implemented by recievers which save last recieved packet,
        and for writers should reset state of the writer
        """
