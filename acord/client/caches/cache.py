# Cache handler for acord
from __future__ import annotations

from typing import Any, Dict, Sequence, Optional
from weakref import WeakValueDictionary
from abc import ABC, abstractmethod
from acord import (
    User,
    Guild,
    Snowflake
)
import pydantic


class CacheSection(ABC, pydantic.BaseModel):
    """An ABC for implementing sections for provided caches,
    this may be useful as you can add constant values per cache section.

    .. warning::
        When implementing with :class:`Cache`, 
        if cache section is not provided,
        we will construct one using limits from the cache.

    Parameters
    ----------
    name: :class:`str`
        Name of section
    data: :obj:`py:weakref.WeakValueDictionary`
        Existing data to cache,
        this is not constant and can be cleared.
    constants: :obj:`py:weakref.WeakValueDictionary`
        Constant values which never change,
        inorder to fetch these values users must use :attr:`CacheSection.constants`
    """
    data: WeakValueDictionary
    name: str
    constants: WeakValueDictionary = WeakValueDictionary()

    @abstractmethod
    def clear(self) -> None:
        """ Clears this cache section """

    def __getattribute__(self, __name: str) -> Any:
        # Allows us to use CacheSection.meth("name")
        # without billions of abstract methods for .data
        # Whilst still allowing us to overwrite said method
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            # Reason we dont use constants is because we want to make sure
            # only the user edits them
            return getattr(self.data, __name)


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
    sections: Dict[str, CacheSection] = {}
    """ Mapping of cache sections for cache """

    def __getitem__(self, item: Any) -> Any:
        return self.sections[item]

    def __delitem__(self, item: Any) -> None:
        del self.sections[item]

    def __len__(self) -> int:
        return len(self.sections)

    def __contains__(self, key: Any) -> bool:
        return key in self.sections

    def __setitem__(self, key: str, value: CacheSection) -> None:
        if value == "*":
            self.sections[key] = CacheSection(
                name=key,
                limit=self.limits[key],
                data=WeakValueDictionary()
            )
        else:
            self.sections[key] = value

    @abstractmethod
    def clear(self) -> None:
        """ Clears the cache, 
        make sure not to erase the constants. """

    # NOTE: Users

    @abstractmethod
    def users(self) -> Sequence[User]:
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
    def add_user(self, user: User) -> None:
        """Adds a :class:`User` to the cache.

        Parameters
        ----------
        user: :class:`User`
            The user to add in the cache.
        """

    @abstractmethod
    def delete_user(self, user_id: Snowflake, /) -> Optional[User]:
        """Removes a :class:`User` from the cache.

        Parameters
        ----------
        user_id: :class:`Snowflake`
            The ID of user to delete.
        """

    # NOTE: Guilds

    @abstractmethod
    def guilds(self) -> Sequence[Guild]:
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
    def add_guild(self, guild: Guild) -> None:
        """Adds a :class:`Guild` to the cache.

        Parameters
        ----------
        guild: :class:`Guild`
            The guild to add in the cache.
        """

    @abstractmethod
    def delete_guild(self, guild_id: Snowflake, /) -> Optional[Guild]:
        """Removes a :class:`Guild` from the cache.

        Parameters
        ----------
        guild_id: :class:`Snowflake`
            The ID of guild to delete.
        """
