# Voice websocket connection
from __future__ import annotations
from typing import Any

from asyncio import AbstractEventLoop
from asyncio.protocols import BaseProtocol
from aiohttp import ClientSession
from traceback import print_exception

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


class VoiceWebsocket(object):
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

    async def upd_connect(self, addr: str, port: int) -> None:
        """ Finishes handshake when connecting to voice """
        acord.logger.debug(f"Attempting to complete UDP connection for conn_id={self._conn_id}")
        transport, protocol = await self._loop.create_datagram_endpoint(
            lambda: DatagramProtocol(self._client, self, self._conn_id),
            remote_addr=(addr, port)
        )
        acord.logger.info(f"Successfully connected to {addr}:{port} for conn_id={self._conn_id}")

        self._sock = (transport, protocol)

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
            if data["op"] == 2:
                self._ready_packet = data
                await self.upd_connect(
                    data["d"]["ip"],
                    data["d"]["port"]
                )
                await self._ws.send_json(self.udp_payload(**kwargs))

    @property
    def guild_id(self) -> str:
        return self._packet["d"]["guild_id"]
