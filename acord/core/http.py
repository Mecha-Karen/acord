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

from . import coreABC
from .respDecoders import *
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
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
        reconnect: bool = True,
        wsTimeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(60, connect=None),
        responseDecoder: typing.Callable = None,
        **payloadData
    ) -> None:
        self._session = aiohttp.ClientSession(loop=loop)
        self.wsTimeout = wsTimeout
        
        self._ws_connected = False
        self.reconnectIfFail = reconnect
        self.startingPayloadData = payloadData
        self.responseDecoder = responseDecoder

    def updatePayloadData(self, overwrite: bool = False, **newData) -> None:
        if overwrite:
            self.startingPayloadData = newData
        else:
            self.startingPayloadData = {**self.startingPayloadData, **newData}

    async def _fetchGatewayURL(self, token):
        uri = coreABC.buildURL('gateway', 'bot')
        
        async with self._session.get(uri, headers={'Authorization': f"Bot {token}"}) as resp:
            data = await resp.json()

            return data

    async def _connect(self, token: str, *, 
        encoding: coreABC.GATEWAY_ENCODING, compress: bool = False
    ) -> None:
        respData = await self._fetchGatewayURL(token)
        GATEWAY_WEBHOOK_URL = respData['url']

        if encoding == "JSON":
            handler = JSON
        elif encoding == "ETF":
            handler = ETF
        else:
            raise ValueError('Unknown encoding: %s' % encoding)

        GATEWAY_WEBHOOK_URL += f'?v={coreABC.API_VERSION}'
        GATEWAY_WEBHOOK_URL += f'&encoding={encoding.lower()}'

        if compress:
            GATEWAY_WEBHOOK_URL += "&compress=zlib-stream"

        async with self._session.ws_connect(GATEWAY_WEBHOOK_URL) as ws:
            self._ws = ws

            async for message in ws:
                msg = message.data
                if compress:
                    msg = decompressResponse(msg)
                msg = handler(msg)

                print(msg)
