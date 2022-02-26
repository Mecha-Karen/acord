# A simple base client for handling responses from discord
from typing import Any, Coroutine, Dict, Iterator, List, Union, Callable, Optional

import asyncio
import logging
import sys
import traceback

from acord.bases.presence import Presence

from acord.core.abc import Route, API_VERSION
from acord.core.http import HTTPClient
from acord.errors import *
from acord.payloads import (
    StageInstanceCreatePayload,
)
from acord.ext.application_commands import ApplicationCommand, UDAppCommand
from acord.bases import Intents, _C
from acord.models import Message, Snowflake, User, Channel, Guild, Stage
from acord.utils import _d_to_channel

from .shard import Shard
from .caches.cache import Cache
from .caches.default import DefaultCache
from .ratelimiter import GatewayRatelimiter, DefaultGatewayRatelimiter

logger = logging.getLogger(__name__)


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
    presence: :class:`Presence`
        Presence to be sent in the identity packet
    encoding: :class:`str`
        Any of ``ETF`` and ``JSON`` are allowed to be chosen, controls data recieved by discord,
        defaults to ``False``.
    compress: :class:`bool`
        Whether to read compressed stream when receiving requests, defaults to ``False``
    dispatch_on_recv: :class:`bool`
        Whether on_socket_recv should be dispatched
    cache: :class:`Cache`
        Cache for the client to use

        .. versionadded:: 0.2.3a0
    gateway_ratelimiter: :class:`GatewayRatelimiter`
        Gateway ratelimiter for client to use

        .. versionadded:: 0.2.3a0

    Attributes
    ----------
    loop: :class:`~asyncio.AbstractEventLoop`
        Loop client uses
    token: :class:`str`
        Token set when initialising class
    dispatch_on_recv: :class:`bool`
        Whether the on_socket_recv should be dispatched
    intents: Union[:class:`Intents`, :class:`int`]
        Intents set when intialising class
    presence: :class:`Presence`
        Presence to be sent in the identity packet
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
    application_commands: Dict[str, List[:class:`UDAppCommand`]]
        Mapping of registered application commands
    shards: List[:class:`Shard`]
        List of shards client is handling

        .. versionadded:: 0.2.3a0
    cache: :class:`Cache`
        Cache of gateway objects, 
        recomended to fetch using built in methods,
        e.g. :meth:`Client.get_user`.

        .. versionadded:: 0.2.3a0
    gateway_ratelimiter: :class:`GatewayRatelimiter`
        Gateway ratelimiter for client to use,
        we recommend not playing around with this as it may lead to unexpected errors

        .. versionadded:: 0.2.3a0
    MAX_CONC: :class:`int`
        Number of shards client has
    guilds: List[:class:`Guilds`]
        List of guilds client has access to
    """
    cache: Cache

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        dispatch_on_recv: bool = False,
        intents: Optional[Union[Intents, int]] = 0,
        presence: Presence = None,
        loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
        encoding: Optional[str] = "JSON",
        compress: Optional[bool] = False,
        cache: Cache = DefaultCache(),
        gateway_ratelimiter: GatewayRatelimiter = DefaultGatewayRatelimiter()
    ) -> None:

        self.loop = loop
        self.token = token
        self.dispatch_on_recv = dispatch_on_recv
        self.intents = intents
        self.presence = presence

        self._events = dict()

        # Gateway connection stuff
        self.encoding = encoding
        self.compress = compress

        # Others
        self.session_id = None
        self.gateway_version = None
        self.user = None
        self.application_commands = dict()

        # When connecting to VC, temporarily stores session_id
        self.awaiting_voice_connections = dict()
        self.voice_connections = dict()

        if not isinstance(cache, Cache):
            raise TypeError("Cache must be a subclass of Cache")

        self.cache = cache
        self.gateway_ratelimiter = gateway_ratelimiter

        self.shards = list()
        self.MAX_CONC = 0

    def on(self, name: str, *, once: bool = False) -> Optional[_C]:
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

        events = self._events.get(event_name, list())
        func: Callable[..., Coroutine] = getattr(self, func_name, None)
        to_rmv: List[Dict] = list()
        tsk = None

        if func:
            try:
                tsk = self.loop.create_task(
                    func(*args, **kwargs), name=f"Acord event dispatch: {event_name}"
                )
            except Exception as exc:
                self.on_error(f"{func} ({func_name})", tsk)

        to_rmv: List[Dict] = list()
        for event in events:
            func = event["func"]
            try:

                # Handle wait for events
                try:
                    fut, check = func
                except (ValueError, TypeError):
                    tsk = self.loop.create_task(
                        func(*args, **kwargs),
                        name=f"Acord event dispatch: {event_name}",
                    )
                else:
                    if check(*args, **kwargs) is True:
                        res = tuple(args) + tuple(kwargs.values())

                        fut.set_result(res)
                        to_rmv.append(event)

            except Exception:
                self.on_error(f"{func} ({func_name})", tsk)
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

        logger.info("Dispatched event: {}".format(event_name))

    def wait_for(
        self, event: str, *, check: Callable[..., bool] = None, timeout: int = None
    ) -> _C:
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

    async def create_stage_instance(self, *, reason: str = None, **data) -> Stage:
        """|coro|

        Creates a stage instance

        Parameters
        ----------
        channel_id: :class:`Snowflake`
            ID of channel to create stage instance,
            channel type must be :attr:`ChannelTypes.GUILD_STAGE_VOICE`
        topic: :class:`str`
            The topic of the Stage instance (1-120 characters)
        privacy_level: :class:`StagePrivacyLevel`
            The privacy level of the Stage instance (default GUILD_ONLY)
        """
        payload = StageInstanceCreatePayload(**data)
        bucket = dict(channel_id=payload.channel_id)
        headers = {"Content-Type": "application/json"}

        if reason is not None:
            headers["X-Audit-Log-Reason"] = reason

        r = await self.http.request(
            Route("POST", path=f"/stage-instances", bucket=bucket),
            data=payload.json(),
            headers=headers,
        )

        return Stage(conn=self.http, **(await r.json()))

    def register_application_command(
        self,
        command: UDAppCommand,
        *,
        guild_ids: Union[List[int], None] = None,
        extend: bool = True,
    ) -> None:
        """Registers application command internally before client is ran,
        after client is ran this method is redundant.
        Consider using :meth:`Client.create_application_command`.

        Parameters
        ----------
        command: :class:`UDAppCommand`
            .. note::
                :class:`UDAppCommand` represents any class which inherits it,
                this includes SlashBase.
            Command to register internally, to be dispatched.
        guild_ids: Union[List[:class:`int`], None]
            Additional guild IDs to restrict command to,
            if value is set to:
                * ``None``: Reads from class (Default option)
                * ``[]`` (Empty List): Makes it global

            .. note::
                If final value is false,
                command will be registered globally
        extend: :class:`bool`
            Whether to extend current guild ids from the command class
        """
        if guild_ids and extend:
            command.guild_ids = command.guild_ids + guild_ids
        elif guild_ids:
            command.guild_ids = guild_ids
        elif extend == []:
            command.guild_ids = []

        exists = self.application_commands.get(command.name)
        if exists:
            c = []
            if isinstance(exists, list):
                check = any(i for i in exists if i.type == command.type)
                c.extend(exists)
            else:
                check = exists.type == command.type
                c.append(exists)

            if check is True:
                raise ApplicationCommandError("Duplicate application command provided")

        else:
            c = command

        self.application_commands.update({command.name: command})

    async def create_application_command(
        self,
        command: UDAppCommand,
        *,
        guild_ids: Union[List[int], None] = None,
        extend: bool = True,
    ) -> Union[ApplicationCommand, List[ApplicationCommand]]:
        """|coro|

        Creates an application command from a :class:`UDAppCommand` class.

        .. note::
            It can take up to an hour for discord to process the command!

        Parameters
        ----------
        same as :meth:`Client.register_application_command`
        """
        # Add to cache
        self.register_application_command(command, guild_ids=guild_ids, extend=extend)
        d = command.json()

        if not command.guild_ids:
            r = await self.http.request(
                Route("POST", path=f"/applications/{self.user.id}/commands"),
                data=d,  # This is a string
                headers={"Content-Type": "application/json"},
            )
            return ApplicationCommand(conn=self.http, **(await r.json()))

        recvd = []

        for guild_id in set(command.guild_ids):
            r = await self.http.request(
                Route(
                    "POST",
                    path=f"/applications/{self.user.id}/guilds/{guild_id}/commands",
                ),
                data=d,
                headers={"Content-Type": "application/json"},
            )

            app_cmd = ApplicationCommand(conn=self.http, **(await r.json()))
            recvd.append(app_cmd)

        return recvd

    async def bulk_update_global_app_commands(
        self, commands: List[UDAppCommand]
    ) -> None:
        """|coro|

        Updates global application commands in bulk

        Parameters
        ----------
        commands: List[:class:`UDAppCommand`]
            List of application commands to update
        """
        json = f'[{", ".join([i.json() for i in commands])}]'
        # [{..., }, {..., }]

        await self.http.request(
            Route("PUT", path=f"/applications/{self.user.id}/commands"),
            data=json,
            headers={"Content-Type": "application/json"},
        )

    async def bulk_update_guild_app_commands(
        self,
        guild_id: Snowflake,
        commands: List[UDAppCommand],
    ) -> None:
        """|coro|

        Updates application commands for a guild in bulk

        Parameters
        ----------
        guild_id: :class:`Snowflake`
            ID of target guild
        commands: List[:class:`UDAppCommand`]
            List of application commands to update
        """
        json = f'[{", ".join([i.json() for i in commands])}]'

        await self.http.request(
            Route(
                "PUT",
                path=f"/applications/{self.user.id}/guilds/{guild_id}/commands",
                bucket=dict(guild_id=guild_id),
            ),
            data=json,
            headers={"Content-Type": "application/json"},
        )

    async def _bulk_write_app_commands(self, exclude: set) -> None:
        cmds = []
        for name, commands in self.application_commands.items():
            if name in exclude:
                continue

            if isinstance(commands, list):
                cmds.extend(*set(commands))
            else:
                cmds.append(commands)

        partitioned = {"global": []}

        for command in cmds:
            if not command.guild_ids:
                partitioned["global"].append(command)
            else:
                for guild_id in command.guild_ids:
                    if guild_id not in partitioned:
                        partitioned[guild_id] = []

                    partitioned[guild_id].append(command)

        global_ = partitioned.pop("global")
        if global_:
            await self.bulk_update_global_app_commands(global_)

        for guild_id, commands in partitioned.items():
            await self.bulk_update_guild_app_commands(guild_id, commands)

    async def shard_handler(self, *ready_scripts) -> None:
        """|coro|

        Default shard handler,
        doesn't do much except intiate shards and waits till all have been disconnected.
        """
        gateway = await self.http.fetch_gateway()

        GATEWAY_WEBHOOK_URL = gateway["url"]
        GATEWAY_WEBHOOK_URL += f"?v={API_VERSION}"

        if self.compress:
            GATEWAY_WEBHOOK_URL += "&compress=zlib-stream"
        GATEWAY_WEBHOOK_URL += f"&encoding={self.encoding}"

        self.MAX_CONC = gateway["shards"]
        TASK_LIST = []

        for i in range(self.MAX_CONC):
            # shard_id = i
            shard = Shard(
                url=GATEWAY_WEBHOOK_URL,
                shard_id=i,
                num_shards=self.MAX_CONC,
                client=self
            )

            await shard.connect()
            await shard.receive_hello()
            await shard.send_identity(
                self.token, self.intents, self.presence
            )
            
            task = shard.listen(shard=shard)
            TASK_LIST.append(task)

            self.shards.append(shard)

        for script in ready_scripts:
            await script

        await asyncio.gather(*TASK_LIST)

    def run(
        self,
        token: str = None,
        reconnect: bool = True,
        update_app_commands: bool = True,
        exclude_app_cmds: set = set(),
        asyncio_debug: bool = False
    ):
        """Runs client, loop blocking.

        Parameters
        ----------
        token: :class:`str`
            Token to log into discord with,
            if :class:`Client.token` is not None it will be used as a fallback,
            just incase this token fails
        reconnect: :class:`bool`
            Whether to reconnect it first connection fails, 
            defaults to ``True``.
        update_add_commands: :class:`bool`
            Whether to update app commands, *in bulk*.
        exclude_app_cmds: :class:`set`
            A set of app names to stop being updated/created
        asyncio_debug: :class:`bool`
            Whether to enable debugging on the current loop.
        """
        if asyncio_debug:
            self.loop.set_debug(True)

        token = token or self.token

        if not token:
            raise ValueError("No token provided")

        if not hasattr(self, "http"):
            self.http = HTTPClient(self, loop=self.loop, token=self.token)
        
        self.http.client = self

        # Login to create session
        # Also validates token
        try:
            self.loop.run_until_complete(self.http.login(token=token))
        except HTTPException:
            if reconnect:
                # Prevent recursion
                # If cannot login, tries to revert token
                # Logins in again
                # If fails again raises error
                logger.info("Failed to login, reconnecting")
                return self.run(token=token, reconnect=False)
            raise

        self.token = token

        self.loop.run_until_complete(self.shard_handler(
            self._bulk_write_app_commands(exclude_app_cmds)
            if update_app_commands else None
        ))

    async def disconnect(self):
        """|coro|

        Disconnects client from discord, ends:

        * Client spawned sessions
        * Shards
        * Voice Connections
        """  
        logger.info("Disconnected from API, closing any open connections")
        await self.http.disconnect()

        for shard in self.shards:
            await shard.disconnect()

        for _, vc in self.voice_connections.items():
            await vc.disconnect()

    # NOTE: Fetch from cache:

    def get_message(self, channel_id: int, message_id: int) -> Optional[Message]:
        """Returns the message stored in the internal cache, may be outdated"""
        return self.cache.get_message(channel_id, message_id)

    def get_user(self, user_id: int) -> Optional[User]:
        """Returns the user stored in the internal cache, may be outdated"""
        return self.cache.get_user(user_id)

    def get_guild(self, guild_id: int) -> Optional[Guild]:
        """Returns the guild stored in the internal cache, may be outdated"""
        return self.cache.get_guild(guild_id)

    def get_channel(self, channel_id: int) -> Optional[Channel]:
        """Returns the channel stored in the internal cache, may be outdated"""
        return self.cache.get_channel(channel_id)

    # NOTE: Fetch from API:

    async def fetch_user(self, user_id: int) -> Optional[User]:
        """Fetches user from API and caches it"""

        resp = await self.http.request(Route("GET", path=f"/users/{user_id}"))
        user = User(conn=self.http, **(await resp.json()))

        self.cache.add_user(user)
        return user

    async def fetch_channel(self, channel_id: int) -> Optional[Channel]:
        """Fetches channel from API and caches it"""

        resp = await self.http.request(Route("GET", path=f"/channels/{channel_id}"))
        channel, _ = _d_to_channel((await resp.json()), self.http)

        self.cache.add_channel(channel)
        return channel

    async def fetch_message(
        self, channel_id: int, message_id: int
    ) -> Optional[Message]:
        """Fetches message from API and caches it"""

        resp = await self.http.request(
            Route("GET", path=f"/channels/{channel_id}/messages/{message_id}")
        )
        message = Message(conn=self.http, **(await resp.json()))

        self.cache.add_message(message)
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

        self.cache.add_guild(guild)

    async def fetch_glob_app_commands(self) -> Iterator[ApplicationCommand]:
        """|coro|

        Fetches all global application commands registered by the client
        """
        r = await self.http.request(
            Route("GET", path=f"/applications/{self.user.id}/commands"),
        )

        for d in await r.json():
            yield ApplicationCommand(conn=self.http, **d)

    async def fetch_glob_app_command(self, command_id: Snowflake) -> ApplicationCommand:
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

    # NOTE: default event handlers

    async def on_voice_server_update(self, vc) -> None:
        """:meta private:"""
        # handles dispatch when client joins VC
        # no need to worry about tasks and threads since this is run as a task
        await vc.connect()
        await vc.listen()

    def on_error(self, event_method, task: asyncio.Task = None):
        """|coro|

        Built in base error handler for events"""
        err = sys.exc_info()
        if task is not None:
            _err = task._exception
            if _err is not None and isinstance(_err, Exception):
                err = (type(_err), _err, _err.__traceback__)

        logger.error('Failed to run event "{}".'.format(event_method), exc_info=err)

        print(f"Ignoring exception in {event_method}", file=sys.stderr)
        traceback.print_exception(*err)
