# Voice websocket connection
from __future__ import annotations

from asyncio import (
    AbstractEventLoop,
    Event
)
import asyncio
from aiohttp import ClientSession, WSMsgType

# For handling voice packets
from struct import pack_into, pack
import nacl.secret
from acord.core.heartbeat import VoiceKeepAlive
from .udp import UDPConnection

from acord.bases import _C

import logging

global CONNECTIONS
CONNECTIONS = 0
logger = logging.getLogger(__name__)


class VoiceWebsocket(object):
    supported_modes = (
        'xsalsa20_poly1305_lite',
        'xsalsa20_poly1305_suffix',
        'xsalsa20_poly1305',
    )

    def __init__(self, 
        voice_packet: dict, 
        loop: AbstractEventLoop, 
        client, 
        channel_id, 
        **kwargs
    ) -> None:
        # Defined in an async enviro so this is fine
        self._session = ClientSession(loop=loop, **kwargs)
        self._packet = voice_packet
        self._connect = False
        self._loop = loop
        self._client = client
        self.channel_id = channel_id

        self._ws = None
        self._keep_alive = None
        self._ready_packet = None
        self._sock = None
        self._listener = None
        self._resume_kwargs = {}

        self.sequence: int = 0
        self.timestamp: int = 0
        self.timeout: float = 0
        self.ssrc: int = 0
        self._lite_nonce: int = 0
        self.mode = None

        self.connect_event = Event()
        self.send_event = Event()
        self.disconnected = False

    async def wait_until_connected(self):
        await self.connect_event.wait()

    async def wait_until_ready(self):
        await self.wait_until_connected()
        await self.send_event.wait()

    async def connect(self, *, v: int = 4) -> None:
        global CONNECTIONS

        # connects to desired endpoint creating new websocket connection
        logger.debug(f"Attempting to connect to {self._packet['d']['endpoint']}")
        ws = await self._session.ws_connect(
           f"wss://{self._packet['d']['endpoint']}?v={v}"
        )
        CONNECTIONS += 1
        self._conn_id = CONNECTIONS
        logger.info(f"Successfully connected to {self._packet['d']['endpoint']}, awaiting UDP handshake")

        self._ws = ws
        self.disconnected = False

    async def disconnect(self, *, message: bytes = b"") -> None:
        if self.disconnected:
            logger.warn(f"Disconnect called on disconnected socket, conn_id={self._conn_id}")
            return
        if not self._keep_alive:
            raise ConnectionError("Keepalive doesn't exist, failed to disconnect ws")

        logger.debug(f"Client disconnected from VC conn_id={self._conn_id}, ending operations")
        self._keep_alive.end()

        try:
            await self._ws.close(code=4000, message=message)
        except Exception:
            pass
        # WS already closed or anything along them lines

        # Disconnect called before sock was intialised
        if self._sock:
            sock = getattr(self._sock, "_sock", f"UDP Socket conn_id={self._conn_id}")
            await self._sock.close()
            logger.info(f"Disconnected from {sock}")

        self._ws = None
        self._sock = None
        self._keep_alive = None

        if self._listener:
            self._listener.cancel("Disconnect called to end conn")
            self._listener = None
            logger.debug("Ended listener task")

        logger.info("Disconnected from voice, Closed ws & socket and ended heartbeats")
        self.disconnected = True

    async def resume(self) -> None:
        # Magic of resuming websocket connections
        # Reconnect
        await self.disconnect()
        await self.connect()

        # Set no identity to True so we can resume
        self._resume_kwargs.update({"no_identity": True})
        await self.listen(**self._resume_kwargs)

        # Resume normally
        await self._ws.send_json({
            "op": 7,
            "d": {
                "server_id": self._packet["d"]["guild_id"],
                "session_id": self._packet["d"]["session_id"],
                "token": self._packet["d"]["token"]
            }
        })
        # Log the result
        logger.info(f"Resuming session for conn_id={self._conn_id}")

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
        self.mode = mode

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

    def checked_add(self, attr, value, limit):
        val = getattr(self, attr)
        if (val + value) > limit:
            setattr(self, attr, 0)
        else:
            setattr(self, attr, (val + value))

    async def upd_connect(self, addr: str, port: int, **kwargs) -> None:
        # Finishes handshake whilst connected to vc
        # self._sock will be a tuple with the transport and protocol

        logger.debug(f"Attempting to complete UDP connection for conn_id={self._conn_id}")
        
        conn = UDPConnection(
            self._ready_packet["d"]["ip"], 
            self._ready_packet["d"]["port"],
            self._loop, **kwargs)
        await conn.connect()

        logger.info(f"Successfully connected to {addr}:{port} for conn_id={self._conn_id}")

        self._sock = conn

    def _get_audio_packet(self, data: bytes) -> bytes:
        header = bytearray(12)
        
        header[0] = 0x80
        header[1] = 0x70

        pack_into('>H', header, 2, self.sequence)
        pack_into('>I', header, 4, self.timestamp)
        pack_into('>I', header, 8, self.ssrc)

        encrypter = getattr(self, f"_encrypt_{self.mode}")
        return encrypter(header, data)

    async def send_audio_packet(self, 
        data: bytes, frames: int,
        *, 
        has_header: bool = False,
        sock_flags: int = 0,
    ) -> None:
        """|coro|

        Sends an audio packet to discord

        Parameters
        ----------
        data: :class:`bytes`
            Bytes of data to send to discord
        has_header: :class:`bool`
            Whether the data has an RTC header attached to it.
            Defaults to False and should only be True if you know what your doing.
        frames: :class:`int`
            Your encoders SAMPLES_PER_FRAME value, 
            used for generating timestamp
        sock_flags: :class:`int`
            Additional flags for the UDP socket
        """
        self.checked_add('sequence', 1, 65535)

        if not has_header:
            data = self._get_audio_packet(data)

        await self._sock.write(data, flags=sock_flags)
        self.checked_add('timestamp', frames, 4294967295)

    async def client_connect(self) -> None:
        await self._ws.send_json({
            "op": 12,
            "d": {
                "audio_ssrc": self.ssrc
            }
        })

        logger.info(f"Sent ssrc for audio conn_id={self._conn_id}")

    async def change_speaking_state(self, flags: int = 1, delay: int = 0) -> None:
        payload = {
            "op": 5,
            "d": {
                "speaking": flags,
                "delay": delay,
            }
        }

        await self._ws.send_json(payload)
        logger.info(f"Updated speaking state for conn_id={self._conn_id}, payload:\n{payload}")

    async def stop_speaking(self) -> None:
        # Stops speaking indicator, should be called after audio transmition
        await self.change_speaking_state(0, 0)
        logger.info(f"Client speaking indicator removed for conn_id={self._conn_id}")

    async def listen(self, **kwargs) -> None:
        """ Begins to listen for websocket events, 
        to terminate this simply end generated task """
        tsk = self._loop.create_task(self._handle_voice(**kwargs))

        self._listener = tsk
        self._resume_kwargs = kwargs

    async def _handle_voice(self, *, after: _C = None, no_identity: bool = False, **kwargs) -> None:
        """ Handles incoming data from websocket """
        if not self._ws:
            raise ValueError("Not established websocket connecting")
        
        if not no_identity:
            # Resume is doing its thing
            await self._ws.send_json(self.identity())
            logger.info(f"Sent identity packet for voice ws conn_id={self._conn_id}")

        while True:
            try:
                message = await self._ws.receive()
            except ConnectionResetError:
                break
            try:
                data = message.json()
            except TypeError:
                # Handling any errors we don't like >:D
                if self._ws._close_code == 4015:
                    await self.resume()
                elif self._ws._close_code == 4014:
                    pass
                elif message.type in (WSMsgType.CLOSED, WSMsgType.CLOSING):
                    logger.warn(f"Voice WS closed for conn_id={self._conn_id}, disconecting shortly")
                elif message.type == WSMsgType.ERROR:
                    logger.error(f"Voice WS for conn_id={self._conn_id} has closed", exc_info=(
                        type(message.extra), message.extra, message.extra.__traceback__
                    ))
                else:
                    logger.info(
                        f"Received invalid json data for voice ws conn_id={self._conn_id},\
                        closing ws, code={self._ws._close_code}")
                
                await self.disconnect()
                break
            except (asyncio.CancelledError, asyncio.TimeoutError):
                logger.warn(f"Voice WS adruptly closed for conn_id={self._conn_id}, ending connection")
                await self.disconnect()
                break

            if data["op"] == 8:
                self._keep_alive = VoiceKeepAlive(self, data)
                self._keep_alive.start()

            if data["op"] == 2:
                self._ready_packet = data
                await self.upd_connect(
                    data["d"]["ip"],
                    data["d"]["port"],
                    client=self._client,
                    vc_Ws=self,
                    conn_id=self._conn_id
                )
                await self._ws.send_json(self.udp_payload(**kwargs))
                self.connect_event.set()

                self.ssrc = data["d"]["ssrc"]

                if after:
                    await after()
                
                # Called so client is ready to send audio without limitations
                await self.client_connect()

            if data["op"] == 4:
                self._decode_key = data["d"]["secret_key"]
                self.send_event.set()

            if data["op"] == 13:
                await self.disconnect()
                break

            if data["op"] == 5:
                await self._client.dispatch("voice_channel_speak", self.channel_id)

    # NOTE: encryption methods

    def _encrypt_xsalsa20_poly1305(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self._decode_key))
        nonce = bytearray(24)
        nonce[:12] = header

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext

    def _encrypt_xsalsa20_poly1305_suffix(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self._decode_key))
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

        return header + box.encrypt(bytes(data), nonce).ciphertext + nonce

    def _encrypt_xsalsa20_poly1305_lite(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self._decode_key))
        nonce = bytearray(24)

        nonce[:4] = pack('>I', self._lite_nonce)
        self.checked_add('_lite_nonce', 1, 4294967295)

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext + nonce[:4]

    # NOTE: properties and what not

    @property
    def guild_id(self) -> str:
        return self._packet["d"]["guild_id"]
