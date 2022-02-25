# Basic ratelimiter for acord
from __future__ import annotations

from typing import Any, List, Tuple

from abc import ABC, abstractmethod
from pydantic import BaseModel
from asyncio import get_event_loop, sleep
import logging


logger = logging.getLogger(__name__)
loop = get_event_loop()


def parse_ratelimit_headers(headers: dict) -> dict:
    """Helper function for extracting ratelimit headers,
    from an api request

    Parameters
    ----------
    headers: :class:`dict`
        Headers received from the response 
    """
    d = {}

    if limit := headers.get("X-RateLimit-Limit"):
        d["limit"] = limit
    if remaining := headers.get("X-RateLimit-Remaining"):
        d["remaining"] = remaining
    if reset := headers.get("X-RateLimit-Reset-After"):
        d["reset"] = reset

    return d


class HTTPRatelimiter(ABC, BaseModel):
    """An ABC for building ratelimiters.

    .. rubric:: Example

    .. code-block:: py

        from acord.core.ratelimiter import Ratelimiter
        from acord.core.http import HTTPClient


        class MyRatelimter(Ratelimiter):
            ## Implement methods

        client = Client(..., )
        client.http = HTTPClient(..., ratelimiter=MyRatelimiter())
    """

    max_requests: Tuple[int, int]
    """ The maximum amount of request allowed to be made in a given timeframe,
    should be in the form (num_requests, time_in_seconds)
    """
    cache: dict = {}
    """ Cache for storing buckets """
    awaiting_requests: List = []
    """ List of coroutines waiting to be called """
    global_lock: bool = False
    """ Whether the client is being ratelimited globally """
    locked_until: int = None
    """ Time in seconds till the ratelimit is over, global only """

    def __init__(self, **kwds) -> None:
        super().__init__(**kwds)

    @abstractmethod
    def increment(self, bucket: str, /) -> None:
        """Increments the current number of requests,
        this should only be called when you have made a request.

        Parameters
        ----------
        bucket: :class:`str`
            Bucket to increment
        """

    @abstractmethod
    def add_bucket(self, bucket: str, data: dict, /) -> None:
        """Adds a new bucket to the cache

        Parameters
        ----------
        bucket: :class:`str`
            Bucket to add
        data: :class:`dict`
            Additional info such as limit and resets
        """

    @abstractmethod
    def bucket_is_limited(self, bucket: str, /) -> bool:
        """Checks if a bucket has been ratelimited.
        Should only be implemented for HTTP Ratelimiters,
        for gateways simply raise NotImplemented

        Parameters
        ----------
        bucket: :class:`str`
            Bucket to check
        """
    
    @abstractmethod
    async def hold_bucket(self, bucket: str, /) -> None:
        """Waits until this bucket is no longer ratelimited

        Parameters
        ----------
        bucket: :class:`str`
            Bucket to wait for
        """

    @abstractmethod
    def global_lock_set(self, released_at: int, /) -> None:
        """Sets the global lock

        Parameters
        ----------
        released_at: :class:`int`
            Time in seconds till lock is lifted 
        """

    @abstractmethod
    async def hold_global_lock(self) -> None:
        """Waits until the global ratelimit is over"""

    @abstractmethod
    def should_lock(self) -> bool:
        """ Checks whether requests should be locked """

# Default implementations

class DefaultHTTPRatelimiter(HTTPRatelimiter):
    current_requests: int = 0
    global_lock: Any = None

    def increment(self, bucket: str, /) -> None:
        self.current_requests += 1

        if not (bucket := self.cache.get(bucket)):
            bucket["remaining"] -= 1

    def add_bucket(self, bucket: str, data: dict, /) -> None:
        self.cache[bucket] = data

    def bucket_is_limited(self, bucket: str, /) -> bool:
        bucket = self.cache.get(bucket)

        if not bucket:
            return False

        if ((bck := bucket.get("task")) is not None) or bucket["remaining"] <= 0:
            if not bck:
                task = loop.create_task(self._release_bucket_ratelimit_task(bucket))
                bucket["task"] = task

            return True
        return False

    async def hold_bucket(self, bucket: str, /) -> None:
        bucket = self.cache.get(bucket)

        if not bucket:
            return

        task = bucket.get(task)

        if not task:
            return

        logger.info(f"Bucket {bucket:<20} has been ratelimited, waiting")

        await task

    def global_lock_set(self, released_at: int, /) -> None:
        if self.global_lock is True:
            raise RuntimeError("Lock has already been set")
        
        self.global_lock = True
        self.locked_until = released_at

        self.global_task = loop.create_task(self._def_release_global_lock_task())

    async def hold_global_lock(self) -> None:
        if self.global_lock:
            return
        logger.info("REST Api has been ratelimited globally, waiting")

        await self.global_task

    def should_lock(self) -> bool:
        if self.current_requests >= self.max_requests[0]:
            return True
        return False

    async def _reset_requests_task(self) -> None:
        while True:
            await sleep(self.max_requests[1])

            self.current_requests = 0

    async def _release_global_lock_task(self) -> None:
        await sleep(self.locked_until)

        self.locked_until = None
        self.global_lock = False

    async def _release_bucket_ratelimit_task(self, bucket: str) -> None:
        bucket = self.cache.get(bucket)

        if not bucket:
            return

        await sleep(bucket["reset"])
        bucket["task"] = None
