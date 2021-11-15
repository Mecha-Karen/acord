import json
import zlib

ZLIB_SUFFIX = b'\x00\x00\xff\xff'
INFLATOR = zlib.decompressobj()
BUFFER = bytearray()


def decompressResponse(msg):
    if type(msg) is bytes:
        BUFFER.extend(msg)

        if len(msg) < 4 or msg[-4:] != b'\x00\x00\xff\xff':
            return
        msg = INFLATOR.decompress(BUFFER)
        msg = msg.decode('utf-8')
        BUFFER.clear()

    return msg


def ETF(msg):
    raise NotImplementedError()


def JSON(msg):
    return json.loads(msg)
