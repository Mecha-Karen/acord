# A simple base client for handling responses from discord
import asyncio
import warnings
import acord
import sys
import traceback
from inspect import iscoroutinefunction
from functools import wraps

from acord.core.decoders import ETF, JSON, decompressResponse
from acord.core.signals import gateway

from ..core.http import HTTPClient
from ..errors import *

from typing import (
    Union, Callable
)

from acord.models import User


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
    def __init__(self, *,
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
        token: str = None,
        encoding: str = "JSON",
        compress: bool = False,
        commandHandler: Callable = None,
    ) -> None:

        self.loop = loop
        self.token = token

        self._events = dict()
        self.commandHandler = commandHandler

        # Gateway connection stuff
        self.encoding = encoding
        self.compress = compress

        # Others
        self.session_id = None
        self.gateway_version = None
        self.user = None

    def bindToken(self, token: str) -> None:
        self._lruPermanent = token

    def event(self, func):
        if not iscoroutinefunction(func):
            raise ValueError('Provided function was not a coroutine')
        
        eventName = func.__qualname__
        if eventName in self._events:
            self._events[eventName].append(func)
        else:
            self._events.update({eventName: [func]})

        return func

    def on_error(self, event_method):
        acord.logger.error('Failed to run event "{}".'.format(event_method))

        print(f'Ignoring exception in {event_method}', file=sys.stderr)
        traceback.print_exc()

    async def dispatch(self, event_name: str, *args, **kwargs) -> None:
        if not event_name.startswith('on_'):
            event_name = 'on_' + event_name
        acord.logger.info('Dispatching event: {}'.format(event_name))

        events = self._events.get(event_name, [])
        acord.logger.info('Total of {} events found for {}'.format(len(events), event_name))
        for event in events:
            try:
                await event(*args, **kwargs)
            except Exception:
                self.on_error(event)

    async def handle_websocket(self, ws):
        async for message in ws:
            await self.dispatch('socket_recieve')

            data = message.data
            if type(data) is bytes:
                data = decompressResponse(data)
            
            if not data:
                continue

            if not data.startswith('{'):
                data = ETF(data)
            else:
                data = JSON(data)

            if data['op'] == gateway.INVALIDSESSION:
                acord.logger.error('Invalid Session - Reconnecting Shortly')
                raise GatewayConnectionRefused('Invalid session data, currently not handled in this version')

            if data['t'] == 'READY':
                await self.dispatch('ready')

                self.session_id = data['d']['session_id']
                self.gateway_version = data['d']['v']
                self.user = User(**data['d']['user'])

                continue

            if data['op'] == gateway.HEARTBEATACK:
                await self.dispatch('heartbeat')

    def resume(self):
        """ Resumes a closed gateway connection """

    def run(self, token: str = None, *, reconnect: bool = True):
        if (token or self.token) and getattr(self, '_lruPermanent', False):
            warnings.warn("Cannot use current token as another token was binded to the client", CannotOverideTokenWarning)
        token = getattr(self, '_lruPermanent', None) or (token or self.token)

        if not token:
            raise ValueError('No token provided')

        self.http = HTTPClient(loop=self.loop)
        self.token = token

        # Login to create session
        self.loop.run_until_complete(self.http.login(token=token))

        coro = self.http._connect(
            token,
            encoding=self.encoding, 
            compress=self.compress
        )

        # Connect to discord, send identity packet + start heartbeat
        ws = self.loop.run_until_complete(coro)
        
        self.loop.run_until_complete(self.dispatch('connect'))
        acord.logger.info('Connected to websocket')

        self.loop.run_until_complete(self.handle_websocket(ws))
