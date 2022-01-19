# Refactored code from "discord/opus.py"
# Source: https://github.com/Rapptz/discord.py/

from __future__ import annotations
from typing import Callable, Optional

import ctypes
import ctypes.util
import os
import struct
import array
import sys
import logging
import pydantic
import math
from enum import Enum

from acord import __file__ as file_loc
from acord.errors import VoiceError

logger = logging.getLogger(__name__)

# Encoder CTLs:
APPLICATION_AUDIO    = 2049
APPLICATION_VOIP     = 2048
APPLICATION_LOWDELAY = 2051

CTL_SET_BITRATE      = 4002
CTL_SET_BANDWIDTH    = 4008
CTL_SET_FEC          = 4012
CTL_SET_PLP          = 4014
CTL_SET_SIGNAL       = 4024

# Decoder CTLs:
CTL_SET_GAIN             = 4034
CTL_LAST_PACKET_DURATION = 4039

# Other pointers
c_int16_ptr = ctypes.c_int16()


class BandCtl(int, Enum):
    narrow = 1101
    medium = 1102
    wide = 1103
    superwide = 1104
    full = 1105


class SignalCtl(int, Enum):
    auto = -100
    voice = 3001
    music = 3002


if sys.platform == "win32":
    if struct.calcsize("P") * 8 > 32:
        dll = "voice/opus/libopus-0.x64.dll"
    else:
        dll = "voice/opus/libopus-0.x86.dll"

    current_dir = os.path.dirname(file_loc)
    file_loc = os.path.join(current_dir, dll)
else:
    file_loc = ctypes.util.find_library("opus")

opus = ctypes.cdll.LoadLibrary(file_loc)
logger.info(f"Loaded OPUS library from: {file_loc}")


def gen_opus(file_loc: str = file_loc) -> ctypes.CDLL:
    return ctypes.cdll.LoadLibrary(file_loc)


class OpusConfig(pydantic.BaseModel):
    SAMPLING_RATE: int = 48000
    CHANNELS: int = 2
    FRAME_LENGTH: int = 20  # in ms
    SAMPLE_SIZE: int = struct.calcsize('h') * CHANNELS
    SAMPLES_PER_FRAME: int = int(SAMPLING_RATE / 1000 * FRAME_LENGTH)
    FRAME_SIZE: int = SAMPLES_PER_FRAME * SAMPLE_SIZE
    APPLICATION: int = 2049


class Encoder(object):
    """Default encoder for opus"""
    def __init__(self, *,
        opus: ctypes.CDLL = opus, 
        opus_config: OpusConfig = None,
        def_h: Callable[[Encoder], None] = None,
        **kwargs
    ) -> None:
        self.lib = opus
        self.config = opus_config or OpusConfig(**kwargs)

        self._state = self._create_state()

        if def_h is not None:
            def_h(self)
        else:
            self.set_defaults()

    def set_defaults(self):
        self.set_bitrate(128)
        self.set_fec(True)
        self.set_expected_packet_loss_percent(0.15)
        self.set_bandwidth(BandCtl.full)
        self.set_signal_type(SignalCtl.auto)

    def __del__(self) -> None:
        if hasattr(self, '_state'):
            self.lib.opus_encoder_destroy(self._state)
            self._state = None

    def _create_state(self):
        ret = ctypes.c_int()
        return self.lib.opus_encoder_create(
            self.config.SAMPLING_RATE, 
            self.config.CHANNELS, 
            self.application, 
            ctypes.byref(ret)
        )

    def set_bitrate(self, kbps: int) -> int:
        kbps = min(512, max(16, int(kbps)))

        self.lib.opus_encoder_ctl(self._state, CTL_SET_BITRATE, kbps * 1024)
        return kbps

    def set_bandwidth(self, req: BandCtl) -> None:
        if isinstance(req, str):
            req = getattr(SignalCtl, req)
        elif isinstance(req, int):
            req = SignalCtl(req)

        k = req.value
        self.lib.opus_encoder_ctl(self._state, CTL_SET_BANDWIDTH, k)

    def set_signal_type(self, req: SignalCtl) -> None:
        if isinstance(req, str):
            req = getattr(SignalCtl, req)
        elif isinstance(req, int):
            req = SignalCtl(req)

        k = req.value
        self.lib.opus_encoder_ctl(self._state, CTL_SET_SIGNAL, k)

    def set_fec(self, enabled: bool = True) -> None:
        self.lib.opus_encoder_ctl(self._state, CTL_SET_FEC, 1 if enabled else 0)

    def set_expected_packet_loss_percent(self, percentage: float) -> None:
        self.lib.opus_encoder_ctl(
            self._state, 
            CTL_SET_PLP, 
            min(100, max(0, int(percentage * 100)))
        )

    def encode(self, pcm: bytes, frame_size: int) -> bytes:
        max_data_bytes = len(pcm)
        pcm_ptr = ctypes.cast(pcm, c_int16_ptr)
        data = (ctypes.c_char * max_data_bytes)()

        ret = self.lib.opus_encode(self._state, pcm_ptr, frame_size, data, max_data_bytes)

        return array.array('b', data[:ret]).tobytes()


class Decoder(object):
    """Default decoder for opus"""
    def __init__(self, *,
        opus: ctypes.CDLL = opus, 
        opus_config: OpusConfig = None, 
        **kwargs
    ) -> None:
        self.lib = opus
        self.config = opus_config or OpusConfig(**kwargs)

        self._state = self._create_state()

    def __del__(self) -> None:
        if hasattr(self, '_state'):
            self.lib.opus_decoder_destroy(self._state)
            self._state = None

    def _create_state(self):
        ret = ctypes.c_int()
        return self.lib.opus_decoder_create(
            self.config.SAMPLING_RATE, 
            self.config.CHANNELS, 
            ctypes.byref(ret)
        )

    def packet_get_nb_frames(self, data: bytes) -> int:
        """Gets the number of frames in an Opus packet"""
        return self.lib.opus_packet_get_nb_frames(data, len(data))

    def packet_get_nb_channels(self, data: bytes) -> int:
        """Gets the number of channels in an Opus packet"""
        return self.lib.opus_packet_get_nb_channels(data)

    def packet_get_samples_per_frame(self, data: bytes) -> int:
        return self.lib.opus_packet_get_samples_per_frame(data, self.config.SAMPLING_RATE)

    def _set_gain(self, adjustment: int) -> int:
        """Configures decoder gain adjustment.
        Scales the decoded output by a factor specified in Q8 dB units.
        This has a maximum range of -32768 to 32767 inclusive, and returns
        OPUS_BAD_ARG (-1) otherwise. The default is zero indicating no adjustment.
        This setting survives decoder reset (irrelevant for now).
        gain = 10**x/(20.0*256)

        (from opus_defines.h)
        """
        return self.lib.opus_decoder_ctl(self._state, CTL_SET_GAIN, adjustment)

    def set_gain(self, dB: float) -> int:
        """Sets the decoder gain in dB, from -128 to 128."""

        dB_Q8 = max(-32768, min(32767, round(dB * 256))) 
        # dB * 2^n where n is 8 (Q8)
        return self._set_gain(dB_Q8)

    def set_volume(self, mult: float) -> int:
        """Sets the output volume as a float percent, i.e. 0.5 for 50%, 1.75 for 175%, etc."""
        return self.set_gain(20 * math.log10(mult))

    def _get_last_packet_duration(self) -> int:
        """Gets the duration (in samples) of the last packet successfully decoded or concealed."""

        ret = ctypes.c_int32()
        self.lib.opus_decoder_ctl(self._state, CTL_LAST_PACKET_DURATION, ctypes.byref(ret))
        return ret.value

    def decode(self, data: Optional[bytes], *, fec: bool = False) -> bytes:
        if data is None and fec:
            raise VoiceError("Invalid arguments: FEC cannot be used with null data")

        if data is None:
            frame_size = self._get_last_packet_duration() or self.SAMPLES_PER_FRAME
            channel_count = self.CHANNELS
        else:
            frames = self.packet_get_nb_frames(data)
            channel_count = self.packet_get_nb_channels(data)
            samples_per_frame = self.packet_get_samples_per_frame(data)
            frame_size = frames * samples_per_frame

        pcm = (ctypes.c_int16 * (frame_size * channel_count))()
        pcm_ptr = ctypes.cast(pcm, c_int16_ptr)

        ret = self.lib.opus_decode(
            self._state, 
            data, 
            len(data) if data else 0, pcm_ptr, frame_size, 
            fec)

        return array.array('h', pcm[:ret * channel_count]).tobytes()
