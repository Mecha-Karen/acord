import zlib
import json

ZLIB_SUFFIX = b"\x00\x00\xff\xff"
INFLATOR = zlib.decompressobj()


def decompressResponse(msg):
    BUFFER = bytearray()

    if type(msg) is bytes:
        BUFFER.extend(msg)

        if len(msg) < 4 or msg[-4:] != b"\x00\x00\xff\xff":
            return
        msg = INFLATOR.decompress(BUFFER)
        msg = msg.decode("utf-8")

    return msg

def decodeResponse(data) -> dict:
    if type(data) is bytes:
        try:
            data = decompressResponse(data)
        except Exception:
            data = None

    if not data:
        return {}

    if not data.startswith("{"):
        data = ETF(data)
    else:
        data = JSON(data)

    return data


def ETF(msg):
    raise NotImplementedError()


def JSON(msg):
    return json.loads(msg)
