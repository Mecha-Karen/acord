from __future__ import annotations
from typing import Optional

from ..core import VoiceWebsocket


class BaseTransport(object):
    def __init__(self, conn: VoiceWebsocket) -> None:
        self.conn = conn
        self.sock = conn._sock

    async def recieve(self, *,
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

    async def send(self, data: bytes, *, flags: int = -1) -> None:
        """|coro|

        Sends data through stream,
        writers must include this method and should make sure each packet has an RTC header.
        To simplify this mess you should call :class:`VoiceWebsocket._get_audio_packet`.

        .. note::
            When implementing writers, 
            big files should be handled by you and for sending "complete" payloads,
            call :class:`VoiceWebsocket.send_audio_packet`.

        Parameters
        ----------
        data: :class:`bytes`
            data to send
        flags: :class:`int`
            additional flags when sending data,
            for UDP socket NOT websocket!
        """
        raise NotImplementedError

    async def close(self) -> None:
        """|coro|

        Closes this transport,
        leaving UDP connection open!

        For recievers this should be set to stop recieving,
        and for writers to close any files + stop writing.
        """
        raise NotImplementedError

    async def cleanup(self) -> None:
        """|coro|
        
        Cleans up any cache, if any.
        Should be implemented by recievers which save last recieved packet
        """
