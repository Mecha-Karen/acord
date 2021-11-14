import zlib

ZLIB_SUFFIX = b'\x00\x00\xff\xff'
INFLATOR = zlib.decompressobj()


def decompressResponse(resp):
    ...


