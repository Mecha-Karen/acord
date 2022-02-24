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
        2,
    )

import asyncio
import typing
import aiohttp
import acord
import sys
import logging

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

logger = logging.getLogger(__name__)


class HTTPClient(object):
    """
    Base client used to connection and interact with the websocket.

    Parameters
    ----------
    loop: :class:`~asyncio.AbstractEventLoop`
        A pre-existing loop for aiohttp to run of, defaults to ``asyncio.get_event_loop()``
    reconnect: :class:`bool`
        Attempt to reconnect to gateway if failed, If set to a integer, it will re-attempt n times.
    **payloadData: :class:`dict`
        A dictionary of payload data to be sent with any request

        .. note::
            This information can be overwritten with each response
    """

    def __init__(
        self,
        client: typing.Any,
        *,
        token: str = None,
        connecter: typing.Optional[aiohttp.BaseConnector] = None,
        wsTimeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(60, connect=None),
        loop: typing.Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
    ) -> None:
        self.client = client
        self.token = token
        self.loop = loop
        self.wsTimeout = wsTimeout
        self.connector = connecter

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

    async def login(self, *, token: str) -> dict:
        """Define a session for the http client to use."""
        self._session = aiohttp.ClientSession(connector=self.connector)

        self.token = token

        try:
            data = await self.request(abc.Route("GET", path="/users/@me"))
            
            logger.info("Client has sucessfully logged in")
        except HTTPException as exc:
            logger.error("Failed to login to discord, improper token passed")
            raise GatewayConnectionRefused("Invalid or Improper token passed") from exc

        return data

    async def logout(self):
        """Logs client out from session"""
        logger.info("Logging user out")
        await self.request(abc.Route("POST", path="/auth/logout"))

    async def fetch_gateway(self):
        route = abc.Route("GET", path=f"/gateway/bot")

        r = await self.request(route)
        return await r.json()

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

        headers["Authorization"] = "Bot " + self.token
        headers["User-Agent"] = self.user_agent

        kwargs = dict()
        kwargs["data"] = data
        kwargs["headers"] = headers

        kwargs.update(addtional_kwargs)

        logger.debug(f"Sending Request: bucket={route.bucket} path={route.path}")
        resp = await self._session.request(method=route.method, url=route.url, **kwargs)
        logger.info(f"Request made at {route.path} returned {resp.status}")

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
