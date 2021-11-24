# A simple base client for handling responses from discord
import asyncio
from asyncio.events import AbstractEventLoop, get_event_loop
import warnings
import acord
import sys
import traceback
from inspect import iscoroutinefunction

from acord.core.http import HTTPClient
from acord.core.signals import gateway
from acord.errors import *

from typing import (
    Any, Coroutine, Union, Callable, Optional
)

from acord import Intents
from acord.bases.mixins import _C, T
from acord.models import Message, User

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
    tokenType: typing.Union[BEARER, BOT]
        The token type, which controls the payload data and restrictions.

        .. warning::
            If BEARER, do not use the `run` method. Your able to access data normally.
    commandHandler: :class:`~typing.Callable`
        An optional command handler, defaults to the built-in handler at :class:`~acord.DefaultCommandHandler`.
        
        **Parameters passed though:**

        * Message: :class:`~acord.Message`
        * UpdatedCache: :class:`bool`
    """

    # SHOULD BE OVERWRITTEN
    INTERNAL_STORAGE: dict

    def __init__(self, *,
        token: Optional[str] = None,

        # IDENTITY PACKET ARGS
        intents: Optional[Union[Intents, int]] = 0,

        loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_event_loop(),
        encoding: Optional[str] = "JSON",
        compress: Optional[bool] = False,
        commandHandler: Optional[_C] = None,
    ) -> None:

        self.loop = loop
        self.token = token

        self.intents = intents

        self._events = dict()
        self.commandHandler = commandHandler

        # Gateway connection stuff
        self.encoding = encoding
        self.compress = compress

        # Others
        self.session_id = None
        self.gateway_version = None
        self.user = None

        self.INTERNAL_STORAGE = dict()

        self.INTERNAL_STORAGE['messages'] = dict()
        self.INTERNAL_STORAGE['users'] = dict()
        self.INTERNAL_STORAGE['guilds'] = dict()

    def bindToken(self, token: str) -> None:
        self._lruPermanent = token

    def on(self, name: str, *, once: bool = False):
        def inner(func):
            data = {
                "func": func,
                "once": once
            }

            if name in self._events:
                self._events[name].append(data)
            else:
                self._events.update({name: [data]})

            func.__event_name__ = name

            return func
        return inner

    async def on_error(self, event_method):
        acord.logger.error('Failed to run event "{}".'.format(event_method))

        print(f'Ignoring exception in {event_method}', file=sys.stderr)
        traceback.print_exc()

    async def dispatch(self, event_name: str, *args, **kwargs) -> None:
        if not event_name.startswith('on_'):
            func_name = 'on_' + event_name
        acord.logger.info('Dispatching event: {}'.format(event_name))

        events = self._events.get(event_name, list())
        func: Callable[..., Coroutine] = getattr(self, func_name, None)

        if func:
            events.append({'func': func, 'once': getattr(func, False)})
        
        to_rmv = list()
        for event in events:
            func = event['func']
            try:
                self.loop.create_task(func(*args, **kwargs), name=f'Acord event dispatch: {event_name}')
            except Exception:
                self.on_error()
            else:
                if event.get('once', False):
                    to_rmv.append(event)
        
        for x in to_rmv:
            events.remove(x)

        if events:
            self._events[event_name] = events
        else:
            if event_name in self._events:
                self._events.pop(event_name)

    def resume(self):
        """ Resumes a closed gateway connection """
        raise NotImplementedError()


    def run(self, token: str = None, *, reconnect: bool = True):
        if (token or self.token) and getattr(self, '_lruPermanent', False):
            warnings.warn("Cannot use current token as another token was binded to the client", CannotOverideTokenWarning)
        token = getattr(self, '_lruPermanent', None) or (token or self.token)

        if not token:
            raise ValueError('No token provided')

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
        
        self.loop.run_until_complete(self.dispatch('connect'))
        acord.logger.info('Connected to websocket')

        try:
            gateway.CURRENT_CONNECTIONS[get_event_loop()] = self.http
            self.loop.run_until_complete(handle_websocket(self, ws))
        except KeyboardInterrupt:
            # Kill connection
            self.loop.run_until_complete(self.http.disconnect())
        finally:
            gateway.CURRENT_CONNECTIONS.pop(get_event_loop(), None)

    def get_message(self, channel_id: int, message_id: int) -> Optional[Message]:
        return self.INTERNAL_STORAGE.get('messages', dict()).get(f'{channel_id}:{message_id}')

    def get_user(self, user_id: int) -> Optional[User]:
        return self.INTERNAL_STORAGE.get('users', dict()).get(user_id)

    def get_guild(self, guild_id: int) -> Optional[Any]:
        return self.INTENRAL_STORAGE.get('guilds', dict()).get(guild_id)
