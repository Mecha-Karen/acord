"""
Main HTTP connection and websocket interaction between discord and your application
"""

try:
    import uvloop

    uvloop.install()
except ImportError:
    import warnings

    warnings.warn(
        "Failed to import UVLoop, it is recommended to install this library. \
            If you are using windows simply ignore this warning.\
            \npip install uvloop",
        ImportWarning,
        stacklevel=2,
    )

import asyncio
import typing
import aiohttp
import acord
import sys

from acord.errors import (
    BadRequest,
    DiscordError,
    Forbidden,
    GatewayConnectionRefused,
    HTTPException,
    NotFound,
)
from . import abc
from .heartbeat import KeepAlive
from .decoders import *
from .signals import gateway

from aiohttp import FormData


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

    def __init__(
        self,
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

        self._browser = "acord"
        self._device = "acord"
        self._os = sys.platform
        self._referrer = None
        self._referring_domain = None

        user_agent = "ACord - https://github.com/Mecha-Karen/ACord {0} Python{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent = user_agent.format(
            acord.__version__, sys.version, aiohttp.__version__
        )

        try:
            self._lock = asyncio.Lock(loop=self.loop)
        except TypeError:
            # Legacy support as loop parameter was dropped in 3.10
            self._lock = asyncio.Lock()
        self.trappedBuckets = dict()

    def getIdentityPacket(self, intents=0):
        if hasattr(intents, "value"):
            # enum.Flag cleanup
            intents = intents.value

        return {
            "op": gateway.IDENTIFY,
            "d": {
                "token": self.token,
                "intents": intents,
                "properties": {
                    "$os": self._os,
                    "$browser": self._browser,
                    "$device": self._device,
                    "$referrer": self._referrer,
                    "$referring_domain": self._referring_domain
                },
            },
        }

    async def login(self, *, token: str) -> None:
        """Define a session for the http client to use."""
        self._session = aiohttp.ClientSession(connector=self.connector)
        ot = self.token

        self.token = token

        try:
            data = await self.request(abc.Route("GET", path="/users/@me"))
        except HTTPException as exc:
            self.token = ot
            acord.logger.error("Failed to login to discord, improper token passed")
            raise GatewayConnectionRefused("Invalid or Improper token passed") from exc

        return data

    async def logout(self):
        """Logs client out from session"""
        await self.request(abc.Route("POST", path="/auth/logout"))

    async def _fetchGatewayURL(self, token):
        uri = abc.buildURL("gateway", "bot")

        async with self._session.get(
            uri, headers={"Authorization": f"Bot {token}"}
        ) as resp:
            data = await resp.json()

            return data

    async def decodeResponse(self, resp):
        if isinstance(resp, aiohttp.WSMessage):
            data = resp.data
        elif isinstance(resp, aiohttp.ClientResponse):
            data = await resp.text()
        else:
            raise TypeError("Invalid response provided")

        if isinstance(data, bytes) or getattr(self, "compress", False):
            data = decompressResponse(data)

        if not data.startswith("{"):
            data = ETF(data)
        else:
            data = JSON(data)

        return data

    async def _connect(
        self, token: str, *, encoding, compress=0, **identityPacketKwargs
    ) -> None:
        if not getattr(self, "_session", False):
            acord.logger.warn(
                "Session not defined, user not logged in. Called login manually"
            )
            await self.login(token=(token or self.token))

        self.encoding = encoding
        self.compress = compress

        respData = await self._fetchGatewayURL(token)
        GATEWAY_WEBHOOK_URL = respData["url"]

        GATEWAY_WEBHOOK_URL += f"?v={abc.API_VERSION}"
        GATEWAY_WEBHOOK_URL += f"&encoding={encoding.lower()}"

        if compress:
            GATEWAY_WEBHOOK_URL += "&compress=zlib-stream"

        acord.logger.info("Generated websocket url: %s" % GATEWAY_WEBHOOK_URL)

        kwargs = {
            "proxy_auth": self.proxy_auth,
            "proxy": self.proxy,
            "max_msg_size": 0,
            "timeout": self.wsTimeout,
            "autoclose": False,
            "headers": {
                "User-Agent": self.user_agent,
            },
            "compress": compress,
        }

        ws = await self._session.ws_connect(GATEWAY_WEBHOOK_URL, **kwargs)

        helloRecv = await ws.receive()
        data = await self.decodeResponse(helloRecv)

        self._ws_connected = True

        self.ws = ws

        # Keep links for API_OBJECTS
        self.ws.client = self
        
        self._keep_alive = KeepAlive(self.getIdentityPacket(**identityPacketKwargs), ws, data)
        self._keep_alive.start()

        return ws

    async def disconnect(self) -> None:
        await self._session.close()

    async def request(
        self,
        route: abc.Route,
        data: dict = None,
        headers: dict = dict(),
        **addtional_kwargs,
    ) -> aiohttp.ClientResponse:
        trapped = self.trappedBuckets.get(route.bucket)
        if trapped:
            await asyncio.sleep(trapped)
            self.trappedBuckets.pop(route.bucket, None)

        url = route.url

        headers["Authorization"] = "Bot " + self.token
        headers["User-Agent"] = self.user_agent

        kwargs = dict()
        kwargs["data"] = data
        kwargs["headers"] = headers

        kwargs.update(addtional_kwargs)

        resp = await self._session.request(method=route.method, url=url, **kwargs)

        if 200 <= resp.status < 300:
            return resp

        respData = await self.decodeResponse(resp)

        if 500 <= resp.status < 600:
            raise DiscordError(str(respData))

        if resp.status == 429:
            retryAfter = respData["retry_after"]
            if respData["global"]:
                async with self._lock.acquire():
                    await asyncio.sleep(retryAfter)

                    self._lock.release()

            else:
                self.trappedBuckets.update({route.bucket: retryAfter})
                await asyncio.sleep(retryAfter)
                self.trappedBuckets.pop(route.bucket, None)

            try:
                return await self.request(route, data, headers, **addtional_kwargs)
            except RuntimeError:
                # Form Data has been processed already
                n_data = FormData()
                n_data._fields = data._fields

                return await self.request(route, n_data, headers, **addtional_kwargs)

        if resp.status == 403:
            raise Forbidden(str(respData), payload=respData, status_code=403)
        if resp.status == 404:
            raise NotFound(str(respData), payload=respData, status_code=404)

        raise BadRequest(str(respData), payload=respData, status_code=resp.status)

    @property
    def connected(self):
        return self._ws_connected
