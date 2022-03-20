# Main RestAPI object
from __future__ import annotations

import asyncio
from typing import (
    Dict, 
    Optional, 
    AsyncIterator,
    List,
    Union
)

from acord import (
    Cache,
    DefaultCache,
    Message,
    Guild,
    User,
    Channel,
    ApplicationCommand,
    Snowflake,
    UDAppCommand,
    InteractionType,
    ApplicationCommandType,
)
from acord.errors import ApplicationCommandError
from acord.models.interaction import Interaction
from acord.rest.abc import InteractionServer
from acord.utils import _d_to_channel
from acord.core.http import HTTPClient
from acord.core.abc import Route

import logging

logger = logging.getLogger(__name__)


def get_slash_options(interaction: Interaction) -> dict:
    data = dict()

    for option in interaction.data.options:
        data.update({option.name: option})
    return data


def get_command(client, name: str, type):
    udac = client.application_commands.get(name)

    if udac is not None:
        if isinstance(udac, list):
            # Use this to find command
            for i in udac:
                if i.type == type:
                    udac = i
                    break

    return udac


async def exec_handler(handler, interaction, option):
    _, dev_handle, on_error = handler.__autocomplete__
    
    try:
        return await handler(interaction, option), dev_handle
    except Exception as exc:
        try:
            await on_error(
                interaction,
                (type(exc), exc, exc.__traceback__)
            )
        except Exception:
            logger.error("Failed to trigger on_error for autocomplete", exc_info=1)
    
    return None, None


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
                  so it is adviced to stay away from the VOICE API.

                  .. note::
                        To receive interactions override the clients `on_interaction_create` function.

        * Interactions: Interactions cannot be received unless you have a running server

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
    server: :class:`InteractionServer`
        An intialised interaction server to use for handling interactions.
        
        If left as ``None``,
        no interactions will be dealt with
    handle_interactions: :class:`bool`
        Whether to parse interactions,
        defaults to ``True``.

        .. warning::
            Setting this to ``False`` will remove the following functionalities:

            * Dispatching application commands
            * Handling autocompletes
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
        http_client: HTTPClient = None,
        server: InteractionServer = None,
        handle_interactions: bool = True,
        **kwds
    ) -> None:
        self.token = token
        self.loop = loop
        self.cache = cache

        self.http = http_client or HTTPClient(
            client=self, token=self.token,
            loop=self.loop, **kwds
        )
        self.http.client = self

        self.handle_interactions = handle_interactions

        self.server = server
        self.application_commands: Dict[str, List[UDAppCommand]] = dict()
        self.user = None

        self._set_up = False
        self.task = None

    async def setup(
        self,
        *,
        exclude: Union[set, dict] = {},
        update_commands: bool = True
    ) -> None:
        """ Setup the object, 
        Should be called before any requests are made
        
        Parameters
        ----------
        exclude: Union[:class:`str`, :class:`dict`]
            A set of commands to exclude.

            .. note::
                If using a dict,
                the key will be the command name and
                the value will the type of command to exclude.
        update_commands: :class:`bool`
            Whether to update commands from :attr:`self.application_commands`
        """
        assert not self._set_up, "Rest API has already been setup"

        await self.http.login()

        if update_commands:
            await self._bulk_write_app_commands(exclude)

        self._set_up = True

    async def close(self):
        await self.http._session.close()

    # Methods for application commands

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
        if guild_ids and (extend and command.extend):
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

    async def _bulk_write_app_commands(self, exclude) -> None:
        cmds = []
        for name, commands in self.application_commands.items():
            if name in exclude:
                if not isinstance(exclude, dict):
                    continue

            if isinstance(commands, list):
                cmds.extend(*set(commands))
            else:
                cmds.append(commands)

        partitioned = {"global": []}

        for command in cmds:
            if command.name in exclude and isinstance(exclude, dict):
                type = exclude[command.name]

                if type == "*" or type == command.type:
                    continue

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

    # Other stuff

    async def on_interaction_create(self, interaction: Interaction, /) -> None:
        return

    async def _dispatch_interaction(self, interaction: Interaction) -> None:
        # Executes slash command internally from an interaction
        if not self.handle_interactions:
            return await self.on_interaction_create(interaction)

        if interaction.type == InteractionType.APPLICATION_COMMAND_AUTOCOMPLETE:
            command = get_command(self, interaction.data.name, interaction.data.type)

            if not command:
                return
            
            handlers = command.__pre_calls__.get("__autocompleters__")

            if handlers is None:
                command.auto_complete_handlers()

                handlers = command.__pre_calls__["__autocompleters__"]

            d = []

            for option in interaction.data.options:
                if not option.focused:
                    continue
                handler = handlers.get("*", handlers.get(option.name))

                if not handler:
                    continue
                result, dev_handled = await exec_handler(handler, interaction, option)

                if dev_handled or not result:
                    continue

                if isinstance(result, list):
                    d.extend(result)
                else:
                    d.append(result)

            await interaction.respond_to_autocomplete(d)

        elif interaction.type == InteractionType.APPLICATION_COMMAND:
            if not command:
                return

            args, kwds = (), {}
            if interaction.data.type == ApplicationCommandType.CHAT_INPUT:
                kwds = get_slash_options(interaction)
            elif interaction.data.type == ApplicationCommandType.MESSAGE:
                message = self.get_message(interaction.channel_id, interaction.data.target_id)
                if not message:
                    message = interaction.data.target_id
                args = (message,)
            else:
                user = interaction.get_user(interaction.data.target_id)
                if not user:
                    user = interaction.data.target_id
                args = (user,)

            fut = self.loop.create_future()
            self.loop.create_task(
                command.dispatcher(interaction, fut, *args, **kwds),
                name=f"app_cmd dispatcher : {command.name}",
            )

            possible_exc = await asyncio.wait_for(fut, None)
            if isinstance(possible_exc, Exception):
                logger.exception(
                    "Failed to run command %s", command.name,
                    exc_info=(
                        type(possible_exc),
                        possible_exc,
                        possible_exc.__traceback__
                    )
                )

        await self.on_interaction_create(interaction)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return
