# Default cache handler for acord
from __future__ import annotations

import typing
from acord.models import (
    Snowflake,
    User
)
from acord.models.guild import Guild

from .cache import CacheData, Cache

SECTIONS = {
    "messages": CacheData(),
    "users": CacheData,
    "guilds": CacheData(),
    "channels": CacheData(),
    "stage_instances": CacheData()
}


class DefaultCache(Cache):
    sections = SECTIONS

    def clear(self):
        for cache in self.sections.values():
            cache.clear()

    def users(self) -> typing.Iterator[User]:
        cache = self["users"]

        return cache.values()

    def get_user(self, user_id: Snowflake, /) -> None:
        if not isinstance(user_id, int):
            raise TypeError("User ID must be an int")

        cache = self["users"]

        return cache.get(user_id)

    def add_user(self, user: User, /) -> None:
        if not isinstance(user, User):
            raise TypeError("User must be an instance of a user object")

        cache = self["users"]

        cache[user.id] = user

    def remove_user(self, user_id: Snowflake, *args) -> None:
        if not isinstance(user_id, int):
            raise TypeError("User ID must be an int")

        cache = self["users"]

        return cache.pop(user_id, *args)

    def guilds(self) -> typing.Iterator[Guild]:
        cache = self["guilds"]

        return cache.values()

    def get_guild(self, guild_id: Snowflake, /):
        if not isinstance(guild_id, int):
            raise TypeError("Guild ID must be an int")
        
        cache = self["guilds"]

        return cache.get(guild_id)

    def add_guild(self, guild: Guild, /) -> None:
        if not isinstance(guild, Guild):
            raise TypeError("guild must be an instance of Guild")
        
        cache = self["guilds"]

        cache[guild.id] = guild

    def remove_guild(self, guild_id: Snowflake, *args) -> typing.Optional[Guild]:
        if not isinstance(guild_id, int):
            raise TypeError("Guild ID must be an int")

        cache = self["guilds"]

        return cache.pop(guild_id, *args)
