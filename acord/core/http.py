from __future__ import annotations

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
    HTTPException,
    NotFound,
)
from acord.models import User
from . import abc
from .decoders import *
from .ratelimiter import DefaultHTTPRatelimiter, HTTPRatelimiter, parse_ratelimit_headers
from aiohttp import FormData

logger = logging.getLogger(__name__)


class HTTPClient(object):
    """
    Base HTTPClient for interacting with the REST API.

    Parameters
    ----------
    client: :class:`Client`
        Client class is attached to
    token: :class:`str`
        Bot token to be used for authorizing requests
    connector: :class:`~aiohttp.BaseConnector`
        Connector be used when creating session
    loop: :obj:`asyncio.AbstractEventLoop`
        Loop to be used
    ratelimiter: :class:`HTTPRatelimiter`
        A ratelimiter for client to use.

    Attributes
    ----------
    client: :class:`Client`
        Client attached to this HTTPClient
    token: :class:`str`
        Token to be used for making HTTP Requests.
    connection: :class:`~aiohttp.BaseConnector`
        A connector class to be used with the session
    ratelimiter: :class:`DefaultHTTPRatelimiter`
        Ratelimiter being used by this HTTPClient
    user_agent: :class:`str`
        Default user agent to be sent with all requests.

        .. note::
            This user agent is unique to this class,
            different HTTPClients may have different user agents.
    """

    def __init__(
        self,
        client: typing.Any,
        *,
        token: str = None,
        connecter: aiohttp.BaseConnector = None,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
        ratelimiter: HTTPRatelimiter = DefaultHTTPRatelimiter(
            max_requests=(10000, (60 * 10))
        )
    ) -> None:
        self.client = client
        self.token = token
        self.loop = loop
        self.connector = connecter
        self.ratelimiter = ratelimiter

        user_agent = "ACord - https://github.com/Mecha-Karen/ACord {0} Python{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent = user_agent.format(
            acord.__version__, sys.version, aiohttp.__version__
        )

    async def login(self, *, token: str = None, **kwds) -> dict:
        """|coro|

        Creates a session for client to use,
        returns user data of client on completation

        Parameters
        ----------
        token: :class:`str`
            Token to overwrite :attr:`HTTPClient.token`,
            becomes default token if token was not provided previously.
        **kwds:
            Any additional kwargs to be passed through :class:`~aiohttp.ClientSession`.

            .. warning::
                You may not include ``connector`` and ``loop`` kwargs.
        """
        self._session = aiohttp.ClientSession(connector=self.connector, loop=self.loop, **kwds)

        self.token = token or self.token

        if not self.token:
            raise 

        try:
            r = await self.request(abc.Route("GET", path="/users/@me"))
            r.raise_for_status()
            
            logger.info("Client has successfully logged in")
        except HTTPException as exc:
            logger.error("Failed to login to discord, improper token passed")
            raise Forbidden("Invalid or Improper token passed") from exc

        user_data = await r.json()
        self.client.user = User(conn=self, **user_data)

        return user_data

    async def logout(self):
        """|coro|
        
        Logs client out from session"""
        logger.info("Logging user out")
        await self.request(abc.Route("POST", path="/auth/logout"))

    async def fetch_gateway(self) -> dict:
        """|coro|

        Fetches the bot gateway,
        returns a :class:`dict` with gateway connection info
        """
        route = abc.Route("GET", path=f"/gateway/bot")

        r = await self.request(route)
        return await r.json()

    async def request(
        self,
        route: abc.Route,
        data: typing.Union[dict, FormData, typing.Any] = None,
        headers: dict = dict(),
        **kwds,
    ) -> aiohttp.ClientResponse:
        """|coro|

        Sends a request to the desired route.

        Parameters
        ----------
        route: :class:`Route`
            Route to send request to
        data: Union[:class:`dict`, :class:`~aiohttp.FormData`, Any]
            Data to be sent with request
        headers: :class:`dict`
            Headers to send with request
        **kwds:
            Additional kwargs to be passed through :meth:`~aiohttp.ClientSession.request`
        """
        if self.ratelimiter.global_lock:
            await self.ratelimiter.hold_global_lock()

        if self.ratelimiter.bucket_is_limited(route.bucket):
            await self.ratelimiter.hold_bucket(route.bucket)

        headers = kwds.pop("headers", None) or headers

        if data is not None:
            kwds["data"] = data

        headers["Authorization"] = "Bot " + self.token
        headers["User-Agent"] = self.user_agent

        kwargs = dict()
        kwargs["headers"] = headers

        kwargs.update(kwds)

        resp = await self._session.request(method=route.method, url=route.url, **kwargs)
        logger.info(f"Request made at {route.path:>20} returned {resp.status}")

        ratelimit_headers = parse_ratelimit_headers(resp.headers)

        if ratelimit_headers:
            self.ratelimiter.add_bucket(route.bucket, ratelimit_headers)

        if 200 <= resp.status < 300:
            return resp

        respData = decodeResponse(await resp.read())

        if 500 <= resp.status < 600:
            raise DiscordError(str(respData))

        if resp.status == 429:
            if respData.get("global", False):
                self.ratelimiter.global_lock_set(respData["retry_after"])
                raise HTTPException(429, "HTTP API is being ratelimited globally")

            else:
                await asyncio.sleep(respData["retry_after"])

            try:
                return await self.request(route, data, headers, **kwds)
            except RuntimeError:
                # Form Data has been processed already
                n_data = FormData()
                n_data._fields = data._fields

                return await self.request(route, n_data, headers, **kwds)

        if resp.status == 403:
            raise Forbidden(str(respData), payload=respData, status_code=403)
        if resp.status == 404:
            raise NotFound(str(respData), payload=respData, status_code=404)

        raise BadRequest(str(respData), payload=respData, status_code=resp.status)

    async def __aenter__(self) -> HTTPClient:
        return self

    async def __aexit__(self, *args) -> None:
        pass
