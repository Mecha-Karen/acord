# Simple wrapper for pyogg.OpusEncoder/OpusDecoder
try:
    from pyogg import OpusEncoder, OpusDecoder
except ImportError:
    OpusEncoder = None
    OpusDecoder = None
