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
    refreshed_at: int = 0
    """ Timestamp of when the ratelimiter was last refreshed at """
    tasks: Dict[str, Any] = {}
    """ A mapping of generated tasks """
    shards: Dict[int, Set[Any]] = {}
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
    def add_shard(self, shard, overwrite: bool = False) -> None:
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

    def __init__(self, **kwds) -> None:
        super().__init__(**kwds)

        loop.create_task(self._reset_requests_task())

    def increment(self, key: int, lock_if_exceed: bool = False) -> None:
        if not key in self.current_requests:
            raise RuntimeError("Unknown ratelimit key provided")

        self.current_requests[key] += 1

        if lock_if_exceed and self.exceeded(key):
            self.lock(key)

    def exceeded(self, key: int) -> bool:
        cur = self.current_requests.get(key)

        if cur is None:
            raise RuntimeError("Unknown ratelimit key provided")

        if self.tasks.get(key, {}).get("lock") is not None or (
            cur >= self.max_requests[0]
        ):
            return True
        return False

    def lock(self, key: int) -> None:
        tasks = self.tasks.get(key, {})

        if tasks.get("lock"):
            raise RuntimeError("This key has already been locked")

        async def future():
            cur = time()
            d = cur - self.refreshed_at

            await sleep(d)

            self.tasks[key].pop("lock")

        task = loop.create_task(future())
        
        if not tasks:
            self.task[key] = {"lock": task}
        else:
            self.tasks[key]["lock"] = task

    async def hold_until_reset(self, key: int) -> None:
        tasks = self.tasks.get(key)

        if not tasks:
            return
        if lock_task := tasks.get("lock"):
            await lock_task
        else:
            futs = self.tasks.get("futures")
            
            if futs:
                await futs[0]
            else:
                # Spawn and wait
                fut = loop.create_future()
                
                if futs is None:
                    self.tasks["futures"] = [fut]
                else:
                    self.tasks["futures"].append(fut)

                await wait_for(fut, timeout=None)

    def add_shard(self, shard, overwrite: bool = False) -> None:
        key = shard.ratelimit_key

        if (shards := self.shards.get(key)):
            if shard in shards and overwrite:
                shards.update((shard, ))
                self.shards[key] = shards
        else:
            self.shards[key] = {shard}

        if key not in self.current_requests:
            self.current_requests[key] = 0

    async def _reset_requests_task(self):
        while True:
            await sleep(self.max_requests[1])

            for key in self.max_requests:
                self.max_requests[key] = 0

            if futs := self.tasks.get("futures"):
                for future in futs:
                    future.set_result(1)

                    self.tasks["futures"].remove(future)
