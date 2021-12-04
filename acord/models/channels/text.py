from __future__ import annotations

from typing import Any, List, Optional, Union
import datetime
import pydantic
from aiohttp import FormData

from acord.core.abc import DISCORD_EPOCH, Route
from acord.models import Message, Snowflake
from acord.payloads import ChannelEditPayload, MessageCreatePayload

from .__main__ import Channel

# Standard text channel in a guild
class TextChannel(Channel):
    guild_id: int
    """ ID of guild were text channel belongs """
    position: int
    """ Text channel position """
    permission_overwrites: List[Any]
    """ Channel Permissions """
    name: str
    """ Name of channel """ 
    topic: Optional[str]
    """ Channel topic """
    nsfw: Optional[bool]
    """ Whether channel is marked as NSFW """
    last_message_id: Optional[int]
    """ Last message in channel, may or may not be valid """
    parent_id: Optional[int]
    """ Category to which the channel belongs to """
    last_pin_timestamp: Optional[datetime.datetime]
    """ Last pinned message in channel, may be None """
    permissions: Optional[str]
    """ String of user permissions """
    rate_limit_per_user: Optional[int]
    """ Channel ratelimit """
    default_auto_archive_duration: Optional[int]
    """ Default time for threads to be archived """

    created_at: Optional[datetime.datetime]
    """ When this channel was created """

    @pydantic.validator("created_at")
    def _validate_snowflake(cls, _, **kwargs) -> Optional[datetime.datetime]:
        if _:
            raise ValueError("Time provided, not able to parse")

        timestamp = ((kwargs["values"]["id"] >> 22) + DISCORD_EPOCH) / 1000

        return datetime.datetime.fromtimestamp(timestamp)

    @pydantic.validate_arguments
    def get_message(self, message_id: Union[Message, Snowflake]) -> Optional[Message]:
        """|func|

        Returns the message stored in the internal cache, may be outdated

        Parameters
        ----------
        message_id: Union[:class:`Message`, :class:`Snowflake`]
            ID of message to get
        """
        return self.conn.client.get_message(channel_id=self.id, message_id=message_id)

    @pydantic.validate_arguments
    async def fetch_message(self, message_id: Union[Message, Snowflake]) -> Optional[Message]:
        """|coro|

        Fetch a message directly from channel

        Parameters
        ----------
        message_id: Union[:class:`Message`, :class:`Snowflake`]
            ID of the message to fetch
        """
        if isinstance(message_id, Message):
            message_id = message_id.id

        bucket = dict(channel_id=self.id, guild_id=self.guild_id)

        resp = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/messages/{message_id}", bucket=bucket)
        )

        message = Message(**(await resp.json()))
        self.conn.client.INTERNAL_STORAGE['messages'].update({f'{self.id}:{message.id}': message})

        return message

    async def edit(self, **options) -> Optional[Channel]:
        """|coro|

        Modifies a guild channel, fires a ``channel_update`` event if channel is updated.

        Parameters
        ----------
        name: :class:`str`
            New name for the channel
        type: Literal[0, 5]
            Change the type for the channel, currently on GUILD_TEXT and GUILD_NEWS is supported
        position: :class:`int`
            Change the position of the channel
        topic: :class:`str`
            Change the channels topic, if you wish to remove it use the :class:`MISSING` class
        nsfw: :class:`bool`
            Whether to mark channel as NSFW
        ratelimit: :class:`int`
            Change ratelimit value for channel
        permission_overwrite: List[Any]
            Currently not available
        category: Union[:class:`int`, CategoryChannel]
            Move the channel to a different category, use :class:`MISSING` for no category
        archive_duration: Literal[0, 60, 1440, 4230, 10080]
            Change the default archive duration on a thread, use :class:`MISSING` or 0 for no timeout
        """
        payload = ChannelEditPayload(**options).dict()
        bucket = dict(channel_id=self.id, guild_id=self.guild_id)

        reason = payload.pop("reason", None)

        # Rest should be standard python vars

        await self.conn.request(
            Route("PATCH", path=f"/channels/{self.id}", bucket=bucket),
            data=payload,
            headers={"X-Audit-Log-Reason": reason},
        )

    @pydantic.validate_arguments
    async def fetch_messages(
        self,
        *,
        around: Optional[Union[Message, int]] = None,
        before: Optional[Union[Message, int]] = None,
        after: Optional[Union[Message, int]] = None,
        limit: Optional[int] = 50,
    ) -> List[Message]:
        """|coro|

        Fetch messages directly from a channel

        Parameters
        ----------
        around: Union[:class:`Message`, :class:`int`]
            get messages around this message ID
        before: Union[:class:`Message`, :class:`int`]
            get messages before this message ID
        after: Union[:class:`Message`, :class:`int`]
            get messages after this message ID
        limit: :class:`int`
            max number of messages to return (1-100).

            Defaults to **50**
        """
        bucket = dict(channel_id=self.id, guild_id=self.guild_id)

        around = getattr(around, 'id', around)
        before = getattr(before, 'id', before)
        after = getattr(after, 'id', after)

        params = {"around": around, "before": before, "after": after, "limit": limit}

        if not 0 < limit < 100:
            raise ValueError('Messages to fetch must be an interger between 0 and 100')

        resp = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/messages", bucket=bucket, **params),
        )

        data = await resp.json()

        messages = list()

        for message in data:
            msg = Message(**message)
            self.conn.client.INTERNAL_STORAGE['messages'].update({f'{self.id}:{msg.id}': msg})
            messages.append(msg)

        return messages

    async def send(self, **data) -> Optional[Message]:
        """|coro|

        Create a new message in the channel

        Parameters
        ----------
        content: :class:`str`
            Message content, must be below ``2000`` chars.
        files: Union[List[:class:`File`], :class:`File`]
            A file or a list of files to be sent. File must not be closed else an error is raised.
        message_reference: Union[:class:`MessageReference`]
            A message to reply to, client must be able to read messages in the channel.
        tts: :class:`bool`
            Whether this is a TTS message
        """
        ob = MessageCreatePayload(**data)

        bucket = dict(channel_id=self.id, guild_id=self.guild_id)
        form_data = FormData()

        if ob.files:
            for index, file in enumerate(ob.files):

                form_data.add_field(
                    name=f'file{index}',
                    value=file.fp,
                    filename=file.filename,
                    content_type="application/octet-stream"
                )
            
        form_data.add_field(
            name="payload_json",
            value=ob.json(exclude={'files'}),
            content_type="application/json"
        )

        if not any(
            i for i in ob.dict() 
            if i in ['content', 'files', 'embeds', 'sticker_ids']
        ):
            raise ValueError('Must provide one of content, file, embeds, sticker_ids inorder to send a message')

        r = await self.conn.request(
            Route("POST", path=f"/channels/{self.id}/messages", bucket=bucket),
            data=form_data
        )

        n_msg = Message(**(await r.json()))
        self.conn.client.INTERNAL_STORAGE['messages'].update({f'{self.id}:{n_msg.id}': n_msg})
        return n_msg