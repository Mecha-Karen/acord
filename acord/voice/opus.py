from __future__ import annotations

import ctypes
import ctypes.util
import os
import struct
import sys
import logging

from acord import __file__ as file_loc

logger = logging.getLogger(__name__)


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


class Encoder(object):
    """Default encoder for opus
    """


class Decoder(object):
    """Default decoder for opus
    """

