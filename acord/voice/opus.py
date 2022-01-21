# Simple wrapper for pyogg.OpusEncoder/OpusDecoder
from __future__ import annotations


class PyOggNotInstalled(object):
    pass


try:
    from pyogg import OpusEncoder, OpusDecoder
except ImportError:
    # Not set to None to prevent inheritance errors
    OpusEncoder = PyOggNotInstalled
    OpusDecoder = PyOggNotInstalled

import pydantic
import struct
from asyncio import get_event_loop


class OpusConfig(pydantic.BaseModel):
    SAMPLING_RATE: int = 48000
    CHANNELS: int = 2
    FRAME_LENGTH: int = (20 / 1000) # in ms
    SAMPLE_SIZE: float = struct.calcsize('h') * CHANNELS
    SAMPLES_PER_FRAME: float = SAMPLING_RATE * FRAME_LENGTH
    FRAME_SIZE: int = int(SAMPLES_PER_FRAME * SAMPLE_SIZE)

    BITRATE: int = 128
    EXPECTED_PACKET_LOSS_PERCENT: float = 0.15
    BANDWIDTH: str = "full"
    SIGNAL_TYPE = "auto"
    APPLICATION = "audio"
    SAMPLE_WIDTH = 16

DEFAULT_CONFIG = OpusConfig()


class Encoder(OpusEncoder):
    def __init__(self, *, config: OpusConfig = DEFAULT_CONFIG) -> None:
        self.config = config
        self.loop = get_event_loop()

        super().__init__()
        self.setup()

    def setup(self):
        super().set_application(self.config.APPLICATION)
        super().set_channels(self.config.CHANNELS)
        super().set_max_bytes_per_frame(self.config.SAMPLE_SIZE)
        super().set_sampling_frequency(self.config.SAMPLING_RATE)
        # NOTE: await further changes from PyOgg for bitrate and other funcs

    async def encode(self, pcm: bytes) -> bytes:
        ef_frame_size = (
            len(pcm)
            // self.config.SAMPLE_WIDTH
            // self.config.CHANNELS
        )

        # if ef_frame_size < self.config.FRAME_SIZE:
            # If frame size is lower then desired config
            # Pad packet with silence
        #     pcm += (
        #         b"\x00"
        #         * ((self.config.FRAME_SIZE - ef_frame_size)
        #             * self.config.SAMPLE_WIDTH
        #             * self.config.CHANNELS)
        #     )

        return await self.loop.run_in_executor(
            None, super().encode, pcm
        )
