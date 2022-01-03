# A simple base client for handling responses from discord
import asyncio
import warnings
import acord
import sys
import traceback

from acord.core.abc import Route
from acord.core.signals import gateway
from acord.core.http import HTTPClient
from acord.errors import *
from acord.payloads import GenericWebsocketPayload

from typing import Any, Coroutine, Dict, List, Tuple, Union, Callable, Optional

from acord.bases import (
    Intents, Presence
)
from acord.models import Message, User, Channel, Guild, TextChannel

# Cleans up client class
from .handler import handle_websocket


class Client(object):
    """
    Client for interacting with the discord API

    Parameters
    ----------
    loop: :class:`~asyncio.AbstractEventLoop`
        An existing loop to run the client off of
    token: :class:`str`
        Your API Token which can be generated at the developer portal
    intents: Union[:class:`Intents`, :class:`int`]
        Intents to be passed through when connecting to gateway, defaults to ``0``
    encoding: :class:`str`
        Any of ``ETF`` and ``JSON`` are allowed to be chosen, controls data recieved by discord,
        defaults to ``False``.
    compress: :class:`bool`
        Whether to read compressed stream when receiving requests, defaults to ``False``

    Attributes
    ----------
    loop: :class:`~asyncio.AbstractEventLoop`
        Loop client uses
    token: :class:`str`
        Token set when initialising class
    intents: Union[:class:`Intents`, :class:`int`]
        Intents set when intialising class
    encoding: :class:`str`
        Encoding set when initialising class
    compress: :class:`bool`
        Whether to read compressed stream when receiving requests
    session_id: :class:`str`
        Session ID recieved when connecting to gateway
    gateway_version: :class:`str`
        Selected gateway version, available after connecting to gateway.
        In form ``v[0-9]``.
    user: :class:`User`
        Client user object
    INTERNAL_STORAGE: :class:`dict`
        Cache of gateway objects, recomended to fetch using built in methods,
        e.g. :meth:`Client.get_user`.
    """

    # SHOULD BE OVERWRITTEN
    INTERNAL_STORAGE: dict

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        # IDENTITY PACKET ARGS
        intents: Optional[Union[Intents, int]] = 0,
        loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
        encoding: Optional[str] = "JSON",
        compress: Optional[bool] = False,
    ) -> None:

        self.loop = loop
        self.token = token

        self.intents = intents

        self._events = dict()

        # Gateway connection stuff
        self.encoding = encoding
        self.compress = compress

        # Others
        self.session_id = None
        self.gateway_version = None
        self.user = None

        self.INTERNAL_STORAGE = dict()

        self.INTERNAL_STORAGE["messages"] = dict()
        self.INTERNAL_STORAGE["users"] = dict()
        self.INTERNAL_STORAGE["guilds"] = dict()
        self.INTERNAL_STORAGE["channels"] = dict()
        
    def bind_token(self, token: str) -> None:
        """Bind a token to the client, prevents new tokens from being set"""
        self._lruPermanent = token

    def on(self, name: str, *, once: bool = False):
        """Register an event to be dispatched on call.

        This is a decorator,
        if you do not want to use the decorator consider trying:

        .. code-block:: py

            from acord import Client
            from xyz import some_event_handler

            client = Client(...)
            client.on("message")(some_event_handler)

        Parameters
        ----------
        name: :class:`str`
            Name of event,
            consider checking out all `events <../events.html>`_
        once: :class:`bool`
            Whether the event should be ran once before being removed.
        check: Callable[..., :class:`bool`]
            Check to be ran before dispatching event
        """

        def inner(func):
            data = {"func": func, "once": once}

            if name in self._events:
                self._events[name].append(data)
            else:
                self._events.update({name: [data]})

            # Tuples from wait_for
            if callable(func):
                try:
                    func.__event_name__ = name
                except AttributeError:
                    func.__dict__.update(__event_name__=name)

                return func

        return inner

    def on_error(self, event_method):
        """|coro|

        Built in base error handler for events"""
        acord.logger.error('Failed to run event "{}".'.format(event_method))

        print(f"Ignoring exception in {event_method}", file=sys.stderr)
        traceback.print_exc()

    def dispatch(self, event_name: str, *args, **kwargs) -> None:
        """Dispatch a registered event

        Parameters
        ----------
        event_name: :class:`str`
            Name of event
        *args, **kwargs
            Additional args or kwargs to be passed through
        """
        if not event_name.startswith("on_"):
            func_name = "on_" + event_name
        acord.logger.info("Dispatching event: {}".format(event_name))

        events = self._events.get(event_name, list())
        func: Callable[..., Coroutine] = getattr(self, func_name, None)
        to_rmv: List[Dict] = list()

        if func:
            self.loop.create_task(
                func(*args, **kwargs), name=f"Acord event dispatch: {event_name}"
            )

        to_rmv: List[Dict] = list()
        for event in events:
            func = event["func"]
            try:

                # Handle wait for events
                try:
                    fut, check = func
                except ValueError:
                    self.loop.create_task(
                        func(*args, **kwargs), name=f"Acord event dispatch: {event_name}"
                    )
                else:
                    if check(*args, **kwargs) is True:
                        res = tuple(args) + tuple(kwargs.values())

                        fut.set_result(res)
                        to_rmv.append(event)

            except Exception:
                self.on_error(f'{func} ({func_name})')
            else:
                if event.get("once", False):
                    to_rmv.append(event)

        for x in to_rmv:
            events.remove(x)

        if events:
            self._events[event_name] = events
        else:
            if event_name in self._events:
                self._events.pop(event_name)

    async def resume(self) -> None:
        """|coro|

        Resumes a closed gateway connection,
        should only be called internally.
        """
        payload = dict(
            op=6,
            d=dict(
                token=self.http.token, session_id=self.session_id, seq=gateway.sequence
            ),
        )

        await self.http.ws.send_json(payload)

    def wait_for(self, event: str, *, check: Callable[..., bool] = None, timeout: int = None) -> Tuple[Any]:
        """|coro|

        Wait for a specific gateway event to occur.

        .. rubric:: Examples

        .. code-block:: py

            # Simple Greeting
            data = Client.wait_for(
                "message", 
                check=lambda message: message.content == "Hello",
                timeout=30.0
            )
            message = data[0]

            return message.reply(content=f"Hello, {message.author}")

        Parameters
        ----------
        event: :class:`str`
            Gateway event to wait for.
        check: Callable[..., :class:`bool`]
            Validate the gateway event recieved
        timeout: :class:`int`
            Time to wait for event to be recieved
        """
        if not check:
            check = lambda *args, **kwargs: True

        fut = self.loop.create_future()

        self.on(event)((fut, check))

        return asyncio.wait_for(fut, timeout=timeout)

    async def change_presence(self, presence: Presence) -> None:
        """|coro|

        Changes client presence

        Parameters
        ----------
        presence: :class:`Presence`
            New presence for client,
            You may want to checkout the guide for presences.
            Which can be found `here <../guides/presence.html>`_.
        """
        payload = GenericWebsocketPayload(
            op=gateway.PRESENCE,
            d=presence
        )

        await self.http.ws.send_str(payload.json())

    def run(self, token: str = None, *, reconnect: bool = True, resumed: bool = False):
        """Runs the client, loop blocking

        Parameters
        ----------
        token: :class:`str`
            Token to be passed through, if binded both :attr:`Client.token` and are overwritten.
            Else, this token will be used to connect to gateway,
            if fails falls back onto :attr:`Client.token`.
        reconnect: :class:`bool`
            Whether to reconnect it first connection fails, defaults to ``True``.
        """
        if (token or self.token) and getattr(self, "_lruPermanent", False):
            warnings.warn(
                "Cannot use current token as another token was binded to the client",
                CannotOverideTokenWarning,
            )
        token = getattr(self, "_lruPermanent", None) or (token or self.token)

        if not token:
            raise ValueError("No token provided")

        if not hasattr(self, "http"):
            self.http = HTTPClient(loop=self.loop, token=self.token)

        self.http.client = self

        self.token = token

        # Login to create session
        try:
            self.loop.run_until_complete(self.http.login(token=token))
        except HTTPException:
            if reconnect:
                # Prevent recursion
                # If cannot login, tries to revert token
                # Logins in again
                # If fails again raises error
                return self.run(token=token, reconnect=False)
            raise

        coro = self.http._connect(
            token,
            encoding=self.encoding,
            compress=self.compress,
            # for identity
            intents=self.intents,
        )

        # Connect to discord, send identity packet + start heartbeat
        ws = self.loop.run_until_complete(coro)

        self.dispatch("connect")
        acord.logger.info("Connected to websocket")

        if resumed:
            self.loop.run_until_complete(self.resume())

        try:
            self.loop.run_until_complete(handle_websocket(self, ws))
        except KeyboardInterrupt:
            # Kill connection
            self.loop.run_until_complete(self.http.disconnect())
        except OSError as e:
            if e.args[0] == 104:
                # kill connection and re-run
                self.loop.run_until_complete(self.http.disconnect())

                return self.run(token=token, reconnect=reconnect, resumed=True)

            raise

    # Fetch from cache:

    def get_message(self, channel_id: int, message_id: int) -> Optional[Message]:
        """Returns the message stored in the internal cache, may be outdated"""
        return self.INTERNAL_STORAGE.get("messages", dict()).get(
            f"{channel_id}:{message_id}"
        )

    def get_user(self, user_id: int) -> Optional[User]:
        """Returns the user stored in the internal cache, may be outdated"""
        return self.INTERNAL_STORAGE.get("users", dict()).get(user_id)

    def get_guild(self, guild_id: int) -> Optional[Guild]:
        """Returns the guild stored in the internal cache, may be outdated"""
        return self.INTERNAL_STORAGE.get("guilds", dict()).get(guild_id)

    def get_channel(self, channel_id: int) -> Optional[Channel]:
        """Returns the channel stored in the internal cache, may be outdated"""
        return self.INTERNAL_STORAGE.get("channels", dict()).get(channel_id)

    # Fetch from API:

    async def fetch_user(self, user_id: int) -> Optional[User]:
        """Fetches user from API and caches it"""
        resp = await self.http.request(Route("GET", path=f"/users/{user_id}"))
        user = User(conn=self.http, **(await resp.json()))
        self.INTERNAL_STORAGE["users"].update({user.id: user})
        return user

    async def fetch_channel(self, channel_id: int) -> Optional[Channel]:
        """Fetches channel from API and caches it"""
        resp = await self.http.request(Route("GET", path=f"/channels/{channel_id}"))
        channel = TextChannel(conn=self.http, **(await resp.json()))
        self.INTERNAL_STORAGE["channels"].update({channel.id: channel})
        return channel

    async def fetch_message(
        self, channel_id: int, message_id: int
    ) -> Optional[Message]:
        """Fetches message from API and caches it"""
        resp = await self.http.request(
            Route("GET", path=f"/channels/{channel_id}/messages/{message_id}")
        )
        message = Message(conn=self.http, **(await resp.json()))
        self.INTERNAL_STORAGE["messages"].update(
            {f"{channel_id}:{message_id}": message}
        )
        return message

    async def fetch_guild(
        self, guild_id: int, *, with_counts: bool = False
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
        self.INTERNAL_STORAGE["guilds"].update({guild.id: guild})

    # Get from cache or Fetch from API:

    async def gof_channel(self, channel_id: int) -> Optional[Any]:
        """Attempts to get a channel, if not found fetches and adds to cache.
        Raises :class:`NotFound` if cannot be fetched"""
        channel = self.get_channel(channel_id)

        if channel is None:
            return await self.fetch_channel(channel_id)
        return channel
    
    @property
    def guilds(self):
        return self.INTERNAL_STORAGE["guilds"]
