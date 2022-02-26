# Basic Gateway Ratelimiter for ACord
from __future__ import annotations
from time import time

from typing import Any, Dict, Optional, Set, Tuple, Type
from types import TracebackType
from abc import ABC, abstractmethod
from pydantic import BaseModel
from asyncio import sleep, get_event_loop, wait_for
import logging

logger = logging.getLogger(__name__)
loop = get_event_loop()


class GatewayRatelimiter(ABC, BaseModel):
    """An ABC for creating gateway ratelimiters.

    .. note::
        This is only used when user sends gateway commands,
        so you don't need to worry about handling data received.

    .. tip::
        Its always smart to leave some requests for heartbeats

    .. rubric:: Working with gateway ratelimiters

    .. code-block:: py

        async with GatewayRatelimiter(..., ) as lock:
            if lock.exceeded(..., ):
                await lock.hold_until_reset(..., )

            lock.increment(..., )
            return await request(..., )
    """
    max_requests: Tuple[int, int]
    """ A tuple containing the limit of requests allowed to be made, (rate, per) """
    current_requests: Dict[int, int] = {}
    """ Mapping of number of requests each ratelimit_key has made """
    blocked: bool = False
    """ Whether to block any requests till reset """
    refreshed_at: int = 0
    """ Timestamp of when the ratelimiter was last refreshed at """
    tasks: Dict[str, Any] = {}
    """ A mapping of generated tasks """
    shards: Dict[int, Set[Any]]
    """ Shards this ratelimiter is attached to,
    a mapping of RATELIMIT_KEY and Set[Shard]
    """

    def __init__(self, **kwds) -> None:
        super().__init__(**kwds)

        self.refreshed_at = time()

    async def __aenter__(self) -> GatewayRatelimiter:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        ...


    @abstractmethod
    def increment(self, key: int, lock_if_exceed: bool = False) -> None:
        """ Increments the total number of requests 
        
        Parameters
        ----------
        key: :class:`int`
            Key that is currently making the request
        lock_if_exceed: :class:`bool`
            Whether to lock the ratelimiter if exceeded
        """

    @abstractmethod
    def exceeded(self, key: int) -> bool:
        """Whether a key has exceeded its requests

        Parameters
        ----------
        key: :class:`int`
            Key to check
        """

    @abstractmethod
    def lock(self, key: int) -> None:
        """ Locks ratelimiter till next refresh 
        
        Parameters
        ----------
        key: :class:`int`
            Key to lock
        """

    @abstractmethod
    async def hold_until_reset(self, key: int) -> None:
        """ |coro|
        
        Blocks until the next reset 
        
        Parameters
        ----------
        key: :class:`int`
            Key to wait for
        """

    @abstractmethod
    def add_shard(self, shard) -> None:
        """Adds a :class:`Shard` to the ratelimiter
        
        Parameters
        ----------
        shard: :class:`Shard`
            Shard to add
        """


## Default implementation

class DefaultGatewayRatelimiter(GatewayRatelimiter):
    max_requests: Tuple[int, int] = (
        (120 - 3),
        60
    )
