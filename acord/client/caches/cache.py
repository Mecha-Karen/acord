# Cache handler for acord
from __future__ import annotations

from typing import Any, Dict, Iterator, Optional
from weakref import WeakValueDictionary
from abc import ABC, abstractmethod
from acord import (
    User,
    Guild,
    Snowflake
)
import pydantic


class CacheData(WeakValueDictionary):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> WeakValueDictionary:
        if isinstance(v, dict):
            return cls(v)
        assert isinstance(v, WeakValueDictionary), "Value must be a weak value dict"

        return v


class Cache(ABC, pydantic.BaseModel):
    """An ABC for implementing caches for acord

    This class can be used to customise caches to the user needs,
    which may include setting limit on each of the caches.

    .. note::
        When redefining limits,
        if any keys are left out we will fill it in with our default values.
        However, if you have already defined a section we will not touch it.

    .. rubric:: Example

    .. code-block:: py

        from acord import Cache, Client

        class MyCache(Cache):
            ## Implement methods

        client = Client(cache=MyCache())
    """
    sections: Dict[str, CacheData] = {}
    """ Mapping of cache sections for cache """

    def __getitem__(self, item: Any) -> Any:
        return self.sections[item]

    def __delitem__(self, item: Any) -> None:
        del self.sections[item]

    def __len__(self) -> int:
        return len(self.sections)

    def __contains__(self, key: Any) -> bool:
        return key in self.sections

    def __setitem__(self, key: str, value: CacheData) -> None:
        self.sections[key] = CacheData.validate(value)

    @abstractmethod
    def clear(self) -> None:
        """ Clears the cache, 
        make sure not to erase the constants. """

    # NOTE: Users

    @abstractmethod
    def users(self) -> Iterator[User]:
        """ Returns all users that are currently cached. """

    @abstractmethod
    def get_user(self, user_id: Snowflake, /) -> Optional[User]:
        """ Gets a :class:`User` from the cache.

        Parameters
        ----------
        user_id: :class:`Snowflake`
            The ID of user to get.
        """

    @abstractmethod
    def add_user(self, user: User, /) -> None:
        """Adds a :class:`User` to the cache.

        Parameters
        ----------
        user: :class:`User`
            The user to add in the cache.
        """

    @abstractmethod
    def remove_user(self, user_id: Snowflake, *args) -> Optional[User]:
        """Removes a :class:`User` from the cache.

        Parameters
        ----------
        user_id: :class:`Snowflake`
            The ID of user to delete.
        """

    # NOTE: Guilds

    @abstractmethod
    def guilds(self) -> Iterator[Guild]:
        """Returns all guilds that are currently cached."""

    @abstractmethod
    def get_guild(self, guild_id: Snowflake, /) -> Optional[Guild]:
        """Gets a :class:`Guild` from the cache.

        Parameters
        ----------
        guild_id: :class:`Snowflake`
            The ID of guild to get.
        """

    @abstractmethod
    def add_guild(self, guild: Guild, /) -> None:
        """Adds a :class:`Guild` to the cache.

        Parameters
        ----------
        guild: :class:`Guild`
            The guild to add in the cache.
        """

    @abstractmethod
    def remove_guild(self, guild_id: Snowflake, *args) -> Optional[Guild]:
        """Removes a :class:`Guild` from the cache.

        Parameters
        ----------
        guild_id: :class:`Snowflake`
            The ID of guild to delete.
        """
