# Cache handler for acord
from __future__ import annotations
from ctypes import Union

from typing import Any, Dict, Iterator, Optional
from abc import ABC, abstractmethod
from weakref import WeakValueDictionary
from acord import (
    User,
    Guild,
    Snowflake,
    Message,
    Channel
)
import pydantic

from acord.models.channels.stage import Stage


class CacheData(dict):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> dict:
        if isinstance(v, (dict, WeakValueDictionary)):
            return v

        raise TypeError("Value must be a dict or WeakValueDictionary")


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

    def __getitem__(self, item: Any) -> CacheData:
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

    # NOTE: Channels

    @abstractmethod
    def channels(self):
        """Returns all channels that are cached"""

    @abstractmethod
    def get_channel(self, channel_id: Snowflake, /) -> Optional[Channel]:
        """Gets a :class:`Channel` from the cache.

        Parameters
        ----------
        channel_id: :class:`Snowflake`
            ID of channel
        """

    @abstractmethod
    def add_channel(self, channel: Channel, /) -> None:
        """Adds a :class:`Channel` to the cache

        Parameters
        ----------
        channel: :class:`Channel`
            Channel to add to cache
        """

    @abstractmethod
    def remove_channel(self, channel_id: Snowflake, *args) -> None:
        """Removes a :class:`Channel` from the cache.

        Parameters
        ----------
        channel_id: :class:`Snowflake`
            ID of channel to remove
        """

    # NOTE: Messages

    @abstractmethod
    def messages(self) -> Iterator[Message]:
        """Returns all messages that are cached"""
    
    @abstractmethod
    def get_message(self, channel_id: Snowflake, message_id: Snowflake, /) -> Optional[Message]:
        """Gets a :class:`Message` from the cache.

        Parameters
        ----------
        channel_id: :class:`Snowflake`
            ID of channel were message is in
        message_id: :class:`Snowflake`
            ID of message to get
        """

    @abstractmethod
    def add_message(self, message: Message, /) -> None:
        """Adds a :class:`Message` to the cache

        Parameters
        ----------
        message: :class:`Message`
            Message to add,
            overwrites if message already exists.
        """

    @abstractmethod
    def remove_message(self, channel_id: Snowflake, message_id: Snowflake, *args) -> Optional[Message]:
        """Removes a :class:`Message` from the cache.

        Parameters
        ----------
        channel_id: :class:`Snowflake`
            ID of channel were message is in
        message_id: :class:`Snowflake`
            ID of message to get
        """

    # NOTE: Stage instances

    @abstractmethod
    def stage_instances(self) -> Iterator[Stage]:
        """Returns all stage instances currently cached"""

    @abstractmethod
    def get_stage_instance(self, id: Snowflake, /) -> Optional[Stage]:
        """Gets a :class:`Stage` from the cache.

        Parameters
        ----------
        id: :class:`Snowflake`
            ID of the stage instance
        """

    @abstractmethod
    def add_stage_instance(self, stage_instance: Stage) -> None:
        """Adds a :class:`Stage` to the cache.

        Parameters
        ----------
        stage_instance: :class:`Stage`
            Stage instance to add
        """

    @abstractmethod
    def remove_stage_instance(self, id: Snowflake, *args) -> Union[Stage, Any]:
        """Removes a :class:`Stage` from the cache

        Parameters
        ----------
        id: :class:`Snowflake`
            ID of the stage instance
        """
