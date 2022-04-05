# Default cache handler for acord
from __future__ import annotations

import typing
from weakref import WeakValueDictionary
from acord.models import Snowflake, User, Guild, Channel, Message, StageInstance

from .cache import CacheData, Cache

SECTIONS = {
    "messages": {},
    "users": WeakValueDictionary(),
    "guilds": {},
    "channels": {},
    "stage_instances": {},
}


class DefaultCache(Cache):
    sections: typing.Dict[str, CacheData] = SECTIONS

    def clear(self):
        for cache in self.sections.values():
            cache.clear()

    def users(self) -> typing.Iterator[User]:
        cache = self["users"]

        return cache.values()

    # NOTE: Users

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

    # NOTE: Guilds

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

    # NOTE: Channels

    def channels(self) -> typing.Iterator[Channel]:
        cache = self["channels"]

        return cache.values()

    def get_channel(self, channel_id: Snowflake, /) -> typing.Optional[Channel]:
        if not isinstance(channel_id, int):
            raise TypeError("Channel ID must be an int")

        cache = self["channels"]

        return cache.get(channel_id)

    def add_channel(self, channel: Channel, /) -> None:
        if not isinstance(channel, Channel):
            raise TypeError("Channel must be an instance of Channel")

        cache = self["channels"]

        cache[channel.id] = channel

    def remove_channel(self, channel_id: Snowflake, *args) -> None:
        if not isinstance(channel_id, int):
            raise TypeError("Channel ID must be an int")

        cache = self["channels"]

        return cache.pop(channel_id, *args)

    # NOTE: Messages

    def messages(self) -> typing.Iterator[Message]:
        cache = self["messages"]

        return cache.values()

    def get_message(
        self, channel_id: Snowflake, message_id: Snowflake, /
    ) -> typing.Optional[Message]:
        if not isinstance(channel_id, int):
            raise TypeError("Channel ID must be an int")
        if not isinstance(message_id, int):
            raise TypeError("Message ID must be an int")

        cache = self["messages"]

        return cache.get(f"{channel_id}:{message_id}")

    def add_message(self, message: Message, /) -> None:
        if not isinstance(message, Message):
            raise TypeError("Message must be an instance of Message")

        cache = self["messages"]

        cache[f"{message.channel_id}:{message.id}"] = message

    def remove_message(
        self, channel_id: Snowflake, message_id: Snowflake, *args
    ) -> typing.Optional[Message]:
        if not isinstance(channel_id, int):
            raise TypeError("Channel ID must be an int")
        if not isinstance(message_id, int):
            raise TypeError("Message ID must be an int")

        cache = self["messages"]

        cache.pop(f"{channel_id}:{message_id}", *args)

    # NOTE: Stage Instances
    def stage_instances(self) -> typing.Iterator[StageInstance]:
        cache = self["stage_instances"]

        return cache.values()

    def get_stage_instance(self, id: Snowflake, /) -> typing.Optional[StageInstance]:
        if not isinstance(id, Snowflake):
            raise TypeError("StageInstance ID must be an int")

        cache = self["stage_instances"]

        return cache.get(id)

    def add_stage_instance(self, stage_instance: StageInstance) -> None:
        if not isinstance(stage_instance, StageInstance):
            raise TypeError("StageInstance instance be an instance of StageInstance")

        cache = self["stage_instances"]

        cache[stage_instance.id] = stage_instance

    def remove_stage_instance(
        self, id: Snowflake, *args
    ) -> typing.Union[StageInstance, typing.Any]:
        if not isinstance(id, Snowflake):
            raise TypeError("StageInstance ID must be an int")

        cache = self["stage_instances"]

        return cache.pop(id, *args)
