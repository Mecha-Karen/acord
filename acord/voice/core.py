# Voice websocket connection
from __future__ import annotations

from asyncio import (
    AbstractEventLoop, 
    BaseProtocol, 
    StreamReader, 
    StreamReaderProtocol, 
    StreamWriter
)
import socket
from aiohttp import ClientSession
from traceback import print_exception

# For handling voice packets
from struct import pack_into, pack
import nacl.secret

from acord.core.heartbeat import VoiceKeepAlive
import acord

global CONNECTIONS


CONNECTIONS = 0


class DatagramProtocol(BaseProtocol):
    __slots__ = ("client", "vc", "_conn")

    def __init__(self, client, vc_Ws, conn):
        self.client = client
        self.vc = vc_Ws
        self._conn = conn

    def datagram_received(self, data, addr):
        acord.logger.debug(f"Recieved data from {addr}:\n{data}")
        self.client.dispatch("udp_recv", self.vc, data, addr)

    def error_received(self, exc):
        acord.logger.error(f"Error raised from conn {self._conn}:\n{exc}")
        print_exception(exc)
        self.client.dispatch("upd_error", self.vc, exc)

    def connection_made(self, transport) -> None:
        acord.logger.debug(f"Connection made, conn_id={self._conn}")
        self.client.dispatch("upd_conn_create", self.vc, transport)

    def connection_lost(self, exc) -> None:
        acord.logger.error(f"Connection lost, conn_id={self._conn}, with exc:\n{exc}")
        self.client.dispatch("upd_conn_lost", self.vc, exc)


class UDPConnection(object):
    def __init__(self, host, port, protocol, loop, **kwds) -> None:
        self.host = host
        self.port = port
        self.loop = loop
        self.proto = protocol(**kwds)
        self.limit = 2 ** 16

        self._sock = None
        self._transport = None
        self._writer = None
        self._reader = None

    async def connect(self) -> None:
        # Creates a UDP connection between host and port
        transport, _ = await self.loop.create_connection(
            lambda: self.proto, self.host, self.port,
            family=socket.SOCK_DGRAM
        )
        self._transport = transport

        reader = StreamReader(limit=self.limit, loop=self.loop)
        protocol = StreamReaderProtocol(reader, loop=self.loop)
        writer = StreamWriter(transport, protocol, reader, self.loop)

        self._writer = writer
        self._reader = reader

    async def send_data(self, data: bytes) -> None:
        await self._writer.write(data)

class VoiceWebsocket(object):
    supported_modes = (
        'xsalsa20_poly1305_lite',
        'xsalsa20_poly1305_suffix',
        'xsalsa20_poly1305',
    )

    def __init__(self, voice_packet: dict, loop: AbstractEventLoop, client, **kwargs) -> None:
        # Defined in an async enviro so this is fine
        self._session = ClientSession(loop=loop, **kwargs)
        self._packet = voice_packet
        self._connect = False
        self._loop = loop
        self._client = client

        self._ws = None
        self._keep_alive = None
        self._ready_packet = None
        self._sock = None

        self.sequence: int = 0
        self.timestamp: int = 0
        self.timeout: float = 0

    async def connect(self, *, v: int = 4) -> None:
        global CONNECTIONS

        # connects to desired endpoint creating new websocket connection
        acord.logger.debug(f"Attempting to connect to {self._packet['d']['endpoint']}")
        ws = await self._session.ws_connect(
           f"wss://{self._packet['d']['endpoint']}?v={v}"
        )
        CONNECTIONS += 1
        self._conn_id = CONNECTIONS
        acord.logger.info(f"Successfully connected to {self._packet['d']['endpoint']}, awaiting UDP handshake")

        self._ws = ws

    async def disconnect(self, *, message: bytes = b"") -> None:
        await self._ws.close(code=4000, message=message)

    def identity(self):
        return {
            "op": 0,
            "d": {
                "server_id": self._packet["d"]["guild_id"],
                "user_id": self._packet["d"]["user_id"],
                "session_id": self._packet["d"]["session_id"],
                "token": self._packet["d"]["token"]
            }
        }

    def udp_payload(self, *, mode: str = None):
        if not mode:
            mode = self._ready_packet["d"]["modes"][0]

        if mode not in self.supported_modes:
            raise ValueError("Encountered unknown mode")

        return {
            "op": 1,
            "d": {
                "protocol": "udp",
                "data": {
                    "address": self._ready_packet["d"]["ip"],
                    "port": self._ready_packet["d"]["port"],
                    "mode": mode
                }
            }
        }

    async def upd_connect(self, addr: str, port: int, *, proto = DatagramProtocol, **kwargs) -> None:
        # Finishes handshake whilst connected to vc
        # self._sock will be a tuple with the transport and protocol

        acord.logger.debug(f"Attempting to complete UDP connection for conn_id={self._conn_id}")
        
        conn = UDPConnection(
            self._ready_packet["d"]["ip"], 
            self._ready_packet["d"]["port"], 
            proto, self._loop, **kwargs)
        await conn.connect()

        acord.logger.info(f"Successfully connected to {addr}:{port} for conn_id={self._conn_id}")

        self._sock = conn

    def _get_audio_packet(self, data: bytes) -> bytes:
        header = bytearray(12)
        
        header[0] = 0x80
        header[1] = 0x70

        pack_into('>H', header, 2, self.sequence)
        pack_into('>I', header, 4, self.timestamp)
        pack_into('>I', header, 8, self.ssrc)

        encrypter = getattr(self, f"_encrypt_{self.chosen_mode}")
        return encrypter(header, data)

    async def send_audio_packet(self, data: bytes, flags: int = 5, *, has_header: bool = False) -> None:
        """|coro|

        Sends an audio packet to discord

        Parameters
        ----------
        data: :class:`bytes`
            Bytes of data to send to discord
        has_header: :class:`bool`
            Whether the data has an RTC header attached to it.
            Defaults to False and should only be True if you know what your doing.
        """
        if not has_header:
            data = self._get_audio_packet(data)

        self._sock.send_data(data)



    async def _handle_voice(self, **kwargs) -> None:
        """ Handles incoming data from websocket """
        if not self._ws:
            raise ValueError("Not established websocket connecting")
        await self._ws.send_json(self.identity())

        async for message in self._ws:
            data = message.json()

            if data["op"] == 8:
                self._keep_alive = VoiceKeepAlive(self._ws, data)
                self._keep_alive.start()
            elif data["op"] == 2:
                self._ready_packet = data
                await self.upd_connect(
                    data["d"]["ip"],
                    data["d"]["port"],
                    client=self._client,
                    vc_Ws=self,
                    conn=self._conn_id
                )
                await self._ws.send_json(self.udp_payload(**kwargs))
            elif data["op"] == 4:
                self._decode_key = data["d"]["secret_key"]
                self.chosen_mode = data["d"]["mode"]
            elif data["op"] == 13:
                acord.logger.debug(f"Client disconnected from VC conn_id={self._conn_id}")
                await self._ws.close()

    # NOTE: encryption methods

    def _encrypt_xsalsa20_poly1305(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = bytearray(24)
        nonce[:12] = header

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext

    def _encrypt_xsalsa20_poly1305_suffix(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

        return header + box.encrypt(bytes(data), nonce).ciphertext + nonce

    def _encrypt_xsalsa20_poly1305_lite(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = bytearray(24)

        nonce[:4] = pack('>I', self._lite_nonce)
        self.checked_add('_lite_nonce', 1, 4294967295)

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext + nonce[:4]

    # NOTE: properties and what not

    @property
    def guild_id(self) -> str:
        return self._packet["d"]["guild_id"]
