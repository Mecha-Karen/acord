# Main RestAPI object
from __future__ import annotations
import asyncio
from typing import Any, Optional, AsyncIterator

from acord import (
    Cache,
    DefaultCache,
    Message,
    Guild,
    User,
    Channel,
    ApplicationCommand,
    Snowflake,
)
from acord.utils import _d_to_channel
from acord.core.http import HTTPClient
from acord.core.abc import Route


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
        self.user = None

        self._set_up = False

    async def setup(self):
        """ Setup the object, 
        Should be called before any requests are made"""
        assert not self._set_up, "Rest API has already been setup"

        await self.http.login()

    # Cache

    def get_message(self, channel_id: int, message_id: int, /) -> Optional[Message]:
        """Returns the message stored in the internal cache, may be outdated"""
        return self.cache.get_message(channel_id, message_id)

    def get_user(self, user_id: int, /) -> Optional[User]:
        """Returns the user stored in the internal cache, may be outdated"""
        return self.cache.get_user(user_id)

    def get_guild(self, guild_id: int, /) -> Optional[Guild]:
        """Returns the guild stored in the internal cache, may be outdated"""
        return self.cache.get_guild(guild_id)

    def get_channel(self, channel_id: int, /) -> Optional[Channel]:
        """Returns the channel stored in the internal cache, may be outdated"""
        return self.cache.get_channel(channel_id)

    # Fetch from API

    async def fetch_user(self, user_id: int, /) -> Optional[User]:
        """Fetches user from API and caches it"""

        resp = await self.http.request(Route("GET", path=f"/users/{user_id}"))
        user = User(conn=self.http, **(await resp.json()))

        self.cache.add_user(user)
        return user

    async def fetch_channel(self, channel_id: int, /) -> Optional[Channel]:
        """Fetches channel from API and caches it"""

        resp = await self.http.request(Route("GET", path=f"/channels/{channel_id}"))
        channel, _ = _d_to_channel((await resp.json()), self.http)

        self.cache.add_channel(channel)
        return channel

    async def fetch_message(self, channel_id: int, message_id: int, /) -> Optional[Message]:
        """Fetches message from API and caches it"""

        resp = await self.http.request(
            Route("GET", path=f"/channels/{channel_id}/messages/{message_id}")
        )
        message = Message(conn=self.http, **(await resp.json()))

        self.cache.add_message(message)
        return message

    async def fetch_guild(
        self, guild_id: int, /, *, with_counts: bool = False
    ) -> Optional[Guild]:
        """Fetches guild from API and caches it.

        .. note::
            If with_counts is set to ``True``, it will allow fields ``approximate_presence_count``,
            ``approximate_member_count`` to be used.
        """

        resp = await self.http.request(
            Route("GET", path=f"/guilds/{guild_id}", with_counts=bool(with_counts)),
        )
        guild = Guild(conn=self.http, **(await resp.json()))

        self.cache.add_guild(guild)
        return guild

    async def fetch_glob_app_commands(self) -> AsyncIterator[ApplicationCommand]:
        """|coro|

        Fetches all global application commands registered by the client
        """
        r = await self.http.request(
            Route("GET", path=f"/applications/{self.user.id}/commands"),
        )

        for d in await r.json():
            yield ApplicationCommand(conn=self.http, **d)

    async def fetch_glob_app_command(self, command_id: Snowflake, /) -> ApplicationCommand:
        """|coro|

        Fetches a global application command registered by the client

        Parameters
        ----------
        command_id: :class:`Snowflake`
            ID of command to fetch
        """
        r = await self.http.request(
            Route("GET", path=f"/applications/{self.user.id}/commands/{command_id}")
        )

        return ApplicationCommand(conn=self.http, **(await r.json()))
