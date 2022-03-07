# Main RestAPI object
from __future__ import annotations
import asyncio
from typing import Any

from acord import (
    Cache,
    DefaultCache
)
from acord.core.http import HTTPClient


class RestApi:
    """Interact with the discord REST API using a standalone object,
    whilst still maintaining an async/await syntax.

    .. warning::
        This object will be used solely for fetching objects and caching whatever you have fetched,
        additional methods for certain routes will be contained within objects.

        .. note::
            This class acts like a mock client for other ACord objects to use.

        .. rubric:: Things not handling by this object

        * Events: Events are not dispatched by this object,
                  so it is adviced to stay away from the VOICE API
        * Interactions: Interactions cannot be received unless :param:`RestApi.server` is provided
                        Servers are ran as a task,
                        so make sure your code doesnt contain anything loop blocking

    Parameters
    ----------
    token: :class:`str`
        Discord **bot** token used to make requests
    loop: :obj:`py:asyncio.AbstractEventLoop`
        Default event loop to use
    cache: :class:`Cache`
        Cache to use to store objects fetched by API
    http_client: Any
        Any object which implements the same functionality as :class:`HTTPClient`
    **kwds:
        Additional kwargs to be passed through :class:`HTTPClient`,
        if it has not been already provided.

        .. DANGER::
            You may not provide the following parameters

            * client
            * token
            * loop
    """
    def __init__(
        self,
        token: str,
        *,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
        cache: Cache = DefaultCache(),
        http_client: Any = None,
        **kwds
    ) -> None:
        self.token = token
        self.loop = loop
        self.cache = cache
        self.http = http_client or HTTPClient(
            client=self, token=self.token,
            loop=self.loop, **kwds
        )
