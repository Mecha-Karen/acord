from __future__ import annotations
from typing import Any, Callable, Union

from io import BufferedIOBase
from os import PathLike
import asyncio

from acord.errors import VoiceError
from acord.bases import File
from .base import BaseTransport

try:
    from acord.voice.core import VoiceConnection
except ImportError:
    VoiceConnection = None
try:
    from acord.voice.opus import Encoder
except ImportError:
    Encoder = None


def getFrameDur(x, y):
    # x -> pcm
    # y -> sampling rate
    return ((x * 10) // (y // 1000)) / 1000


class BasePlayer(BaseTransport):
    def __init__(self, 
        conn: VoiceConnection, 
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

    async def send(self, data: bytes, *, flags: int = 0) -> None:
        if self.closed:
            raise VoiceError("Cannot send bytes through transport as transport is closed")
        encoded_bytes = await self.encoder.encode(data)
        print(encoded_bytes, len(encoded_bytes))

        try:
            await self.conn.send_audio_packet(
                encoded_bytes, self.encoder.config.SAMPLES_PER_FRAME, 
                has_header=False, sock_flags=flags,
            )
        except OSError as exc:
            self.close()
            self._last_send_err = exc
            raise VoiceError("Cannot send bytes through transport", closed=True) from exc

    async def play(self, c_flags: int = 1, delay: int = 5, *, flags: int = 0) -> Union[None, int]:

        await self.conn.change_speaking_state(c_flags, delay)

        async for packet in self:
            try:
                try:
                    await self.send(data=packet, flags=flags)
                except AttributeError:
                    # Socket closed
                    return 1

                await asyncio.sleep(getFrameDur(len(packet), self.encoder.config.SAMPLING_RATE))
            except VoiceError as err:
                if getattr(err, "closed", False):
                    return
                else:
                    raise

            break
        await self.conn.stop_speaking()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        try:
            self.close()
        except VoiceError:
            return
