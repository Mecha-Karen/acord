# A simple base client for handling responses from discord
import asyncio
import typing
import warnings
import acord
import sys
import traceback

from .core.http import HTTPClient
from .errors import *
from functools import wraps

from typing import (
    Union, Callable
)


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

    def bindToken(self, token: str) -> None:
        self._lruPermanent = token

    def event(self, func):
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

    def dispatch(self, event_name: str, *args, **kwargs) -> None:
        if not event_name.startswith('on_'):
            event_name = 'on_' + event_name
        acord.logger.info('Dispatching event: {}'.format(event_name))

        events = self._events.get(event_name, [])
        acord.logger.info('Total of {} events found for {}'.format(len(events), event_name))
        for event in events:
            try:
                fut = event(*args, **kwargs)
            except Exception:
                self.on_error(event)

    async def handle_websocket(self, ws):
        self.dispatch('ready')

        async for message in ws:
            print(message)
            # Il do some actual stuff later

    def run(self, token: str = None, *, reconnect: bool = True):
        if (token or self.token) and getattr(self, '_lruPermanent', False):
            warnings.warn("Cannot use current token as another token was binded to the client", CannotOverideTokenWarning)
        token = getattr(self, '_lruPermanent', None) or (token or self.token)

        if not token:
            raise ValueError('No token provided')

        self.http = HTTPClient(loop=self.loop)

        client = self.loop.run_until_complete(self.http.login(token=token))

        coro = self.http._connect(
            token,
            encoding=self.encoding, 
            compress=self.compress
        )

        ws = self.loop.run_until_complete(coro)
        acord.logger.info('Connected to websocket')

        self.loop.run_until_complete(self.handle_websocket(ws))
