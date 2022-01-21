from __future__ import annotations
from typing import Any, Callable, Union

from io import BufferedIOBase
from os import PathLike

from acord.errors import VoiceError
from acord.bases import File
from .base import BaseTransport

try:
    from acord.voice.core import VoiceWebsocket
except ImportError:
    VoiceWebsocket = None
try:
    from acord.voice.opus import Encoder
except ImportError:
    Encoder = None


class BasePlayer(BaseTransport):
    def __init__(self, 
        conn: VoiceWebsocket, 
        data: Union[BufferedIOBase, PathLike],
        encoder: Encoder = None,
        **encoder_kwargs
    ) -> None:
        if isinstance(data, File):
            data = data.fp

        if not isinstance(data, BufferedIOBase):
            self.fp = open(data, "rb")
            self.pos = 0
        else:
            self.fp = data
            self.pos = data.tell()

        self.index = 0
        self.closed = False
        self.encoder = encoder

        if not self.encoder:
            self.encoder = Encoder(**encoder_kwargs)

        self._last_pack_err = None
        self._last_send_err = None

        super().__init__(conn)

    @property
    def packet_limit(self):
        return self.conn._sock.limit

    def __aiter__(self):
        if self.closed:
            raise VoiceError("Cannot iterate through transport contents as transport is closed")

        return self

    async def __anext__(self):
        try:
            data = self.get_next_packet()
        except EOFError:
            raise StopAsyncIteration

        return data

    def get_next_packet(self):
        self.index += 1
        data = self.fp.read(self.encoder.config.FRAME_SIZE)
        if data == b"":
            self.close()
            raise EOFError("Reached end of file")
        self.pos = self.fp.tell()

        return data

    def close(self) -> None:
        if self.closed:
            raise VoiceError("Transport already closed")

        self.fp.close()
        self.closed = True

    async def cleanup(self) -> None:
        self.fp.seek(0)
        self._last_pack_err = None
        self._last_send_err = None
        self.index = 0

    async def _send(self, data: bytes, *, flags: int = 0) -> None:
        if self.closed:
            raise VoiceError("Cannot send bytes through transport as transport is closed")
        data = await self.encoder.encode(data)

        try:
            await self.conn.send_audio_packet(
                data, has_header=False, sock_flags=flags
            )
        except OSError as exc:
            self.close()
            self._last_send_err = exc
            raise VoiceError("Cannot send bytes through transport", closed=True) from exc

    async def play(self, *, flags: int = 0) -> None:
        await self.conn.wait_until_ready()

        async for packet in self:
            try:
                await self._send(data=packet, flags=flags)
            except VoiceError as err:
                if getattr(err, "closed", False):
                    return
                else:
                    raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        try:
            self.close()
        except VoiceError:
            return
