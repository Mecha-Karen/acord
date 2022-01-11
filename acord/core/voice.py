# Voice websocket connection
from __future__ import annotations
from asyncio import AbstractEventLoop
from aiohttp import ClientSession

from acord.core.heartbeat import VoiceKeepAlive


class VoiceWebsocket(object):
    def __init__(self, voice_packet: dict, loop: AbstractEventLoop, **kwargs) -> None:
        # Defined in an async enviro so this is fine
        self._session = ClientSession(loop=loop, **kwargs)
        self._packet = voice_packet
        self._connect = False
        self._loop = loop

        self._ws = None
        self._keep_alive = None
        self._ready_packet = None

    async def connect(self, *, v: int = 4) -> None:
        # connects to desired endpoint creating new websocket connection
        ws = await self._session.ws_connect(
           f"wss://{self._packet['d']['endpoint']}?v={v}"
        )

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


    async def _handle_voice(self) -> None:
        """ Handles incoming data from websocket """
        if not self._ws:
            raise ValueError("Not established websocket connecting")
        print(self.identity())
        await self._ws.send_json(self.identity())

        async for message in self._ws:
            data = message.json()

            if data["op"] == 8:
                self._keep_alive = VoiceKeepAlive(self._ws, data)
                self._keep_alive.start()
            if data["op"] == 2:
                self._ready_packet = data

    @property
    def guild_id(self) -> str:
        return self._packet["d"]["guild_id"]
