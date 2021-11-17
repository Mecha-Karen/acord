"""
Main HTTP connection and websocket interaction between discord and your application
"""
try:
    import uvloop

    uvloop.install()
except ImportError:
    __import__('warnings').warn('Failed to import UVLoop, it is recommended to install this library\npip install uvloop', ImportWarning)

import asyncio
import typing
import aiohttp
from attr import astuple
import acord
import sys

from acord.errors import GatewayConnectionRefused, HTTPException
from . import helpers
from .heartbeat import KeepAlive
from .decoders import *
from .signals import gateway

class HTTPClient(object):
    """
    Base client used to connection and interact with the websocket.

    Parameters
    ----------
    loop: :class:`~asyncio.AbstractEventLoop`
        A pre-existing loop for aiohttp to run of, defaults to ``asyncio.get_event_loop()``
    reconnect: :class:`bool`
        Attempt to reconnect to gateway if failed, If set to a integer, it will re-attempt n times.
    wsTimeout: :class:`~aiohttp.ClientTimeout`
        Custom timeout configuration for 
    **payloadData: :class:`dict`
        A dictionary of payload data to be sent with any request
        
        .. note::
            This information can be overwritten with each response
    """
    def __init__(self,
        token: str = None,
        connecter: typing.Optional[aiohttp.BaseConnector] = None,
        wsTimeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(60, connect=None),
        proxy: typing.Optional[str] = None,
        proxy_auth: typing.Optional[aiohttp.BasicAuth] = None,
        loop: typing.Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
        unsync_clock: bool = True,

    ) -> None:
        self.token = token
        self.loop = loop
        self.wsTimeout = wsTimeout
        self.connector = connecter
        
        self._ws_connected = False
        self.proxy = proxy
        self.proxy_auth = proxy_auth
        self.use_clock = not unsync_clock

        user_agent = "ACord - https://github.com/Mecha-Karen/ACord {0} Python{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent = user_agent.format(
            acord.__version__, sys.version, aiohttp.__version__
        )
        self._lock = asyncio.Lock(loop=self.loop)

    def getIdentityPacket(self, intents = 0): 
        return {
            "op": gateway.IDENTIFY,
            "d": {
                "token": self.token,
                "intents": intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "acord",
                    "$device": "acord"
                }
            }
        }

    def updatePayloadData(self, overwrite: bool = False, **newData) -> None:
        if overwrite:
            self.startingPayloadData = newData
        else:
            self.startingPayloadData = {**self.startingPayloadData, **newData}

    async def login(self, *, token: str) -> None:
        """ Define a session for the http client to use. """
        self._session = aiohttp.ClientSession(connector=self.connector)
        ot = self.token

        self.token = token

        try:
            data = await self.request(
                helpers.Route("GET", path="/users/@me")
            )
        except HTTPException as exc:
            self.token = ot
            acord.logger.error('Failed to login to discord, improper token passed')
            raise GatewayConnectionRefused('Invalid or Improper token passed') from exc

        return data


    async def _fetchGatewayURL(self, token):
        uri = helpers.buildURL('gateway', 'bot')
        
        async with self._session.get(uri, headers={'Authorization': f"Bot {token}"}) as resp:
            data = await resp.json()

            return data

    async def decodeResponse(self, resp):
        data = resp.data

        if isinstance(data, bytes) or self.compress:
            data = decompressResponse(data)

        if not data.startswith('{'):
            data = ETF(data)
        else:
            data = JSON(data)

    async def _connect(self, token: str, *, 
        encoding, compress = 0,
        **identityPacketKwargs
    ) -> None:
        if not getattr(self, '_session', False):
            acord.logger.warn('Session not defined, user not logged in. Called login manually')
            await self.login(token=(token or self.token))

        self.encoding = encoding
        self.compress = compress

        respData = await self._fetchGatewayURL(token)
        GATEWAY_WEBHOOK_URL = respData['url']

        GATEWAY_WEBHOOK_URL += f'?v={helpers.API_VERSION}'
        GATEWAY_WEBHOOK_URL += f'&encoding={encoding.lower()}'

        if compress:
            GATEWAY_WEBHOOK_URL += "&compress=zlib-stream"

        acord.logger.info('Generated websocket url: %s' % GATEWAY_WEBHOOK_URL)

        kwargs = {
            'proxy_auth': self.proxy_auth,
            'proxy': self.proxy,
            'max_msg_size': 0,
            'timeout': self.wsTimeout,
            'autoclose': False,
            'headers': {
                'User-Agent': self.user_agent,
            },
            'compress': compress
        }

        ws = await self._session.ws_connect(GATEWAY_WEBHOOK_URL, **kwargs)

        helloRecv = await ws.receive()
        data = helloRecv.data

        self._ws_connected = True
        self.ws = ws

        self.loop.create_task(KeepAlive(self.getIdentityPacket(**identityPacketKwargs), ws, data).run())

        return ws

    async def request(self, route: helpers.Route, data: dict = None, **payload) -> None:
        url = route.url

        headers = payload

        headers['Authorization'] = "Bot " + self.token
        headers['User-Agent'] = self.user_agent

        kwargs = dict()
        kwargs['data'] = data
        kwargs['headers'] = headers

        resp = await self._session.request(
            method=route.method,
            url=url,
            **kwargs
        )
        respData = await self.decodeResponse()

        if resp.status == 429:
            retryAfter = respData['retry_after']
            if respData['global']:
                async with self._lock.acquire():
                    await asyncio.sleep(retryAfter)

                    self._lock.release()
            
            else:
                await asyncio.sleep(retryAfter)
            
            return await self.request(route, data, **payload)

        

        return resp
        
    @property
    def connected(self):
        return self._ws_connected
