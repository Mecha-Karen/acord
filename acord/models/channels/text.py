from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Union
import datetime
import pydantic

from acord.core.abc import DISCORD_EPOCH, Route
from acord.models import Message, Snowflake
from acord.payloads import ChannelEditPayload, InviteCreatePayload, ThreadCreatePayload
from acord.utils import _payload_dict_to_json
from acord.errors import APIObjectDepreciated

from .textExt import ExtendedTextMethods
from .base import Channel
from .thread import Thread

# Standard text channel in a guild

async def _pop_task(client, channel_id, *messages) -> None:
    # Create task to pop all messages in bulk deletion
    for message in messages:
        client.INTERNAL_STORAGE['messages'].pop(f'{channel_id}:{message}', None)

class TextChannel(Channel, ExtendedTextMethods):
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
        permission_overwrite: List[:class:`PermissionsOverwrite`]
            List of permissions to overwrite in the channel
        category: Union[:class:`int`, CategoryChannel]
            Move the channel to a different category, use :class:`MISSING` for no category
        archive_duration: Literal[0, 60, 1440, 4230, 10080]
            Change the default archive duration on a thread, use :class:`MISSING` or 0 for no timeout
        """
        payload = ChannelEditPayload(**options).dict()
        bucket = dict(channel_id=self.id, guild_id=self.guild_id)

        keys = list(payload.keys())
        for k in keys:
            if k not in options:
                payload.pop(k)

        reason = payload.pop("reason", None)
        headers = dict()
        if reason:
            headers.update({"X-Audit-Log-Reason": reason})
        headers.update({"Content-Type": "application/json"})

        # Rest should be standard python vars

        await self.conn.request(
            Route("PATCH", path=f"/channels/{self.id}", bucket=bucket),
            data=_payload_dict_to_json(ChannelEditPayload, **payload),
            headers=headers,
        )

    @pydantic.validate_arguments
    async def fetch_messages(
        self,
        *,
        around: Optional[Union[Message, int]] = None,
        before: Optional[Union[Message, int]] = None,
        after: Optional[Union[Message, int]] = None,
        limit: Optional[int] = 50,
    ) -> Iterator[Message]:
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

        around = getattr(around, "id", around)
        before = getattr(before, "id", before)
        after = getattr(after, "id", after)

        params = {"around": around, "before": before, "after": after, "limit": limit}

        if not 0 < limit < 100:
            raise ValueError("Messages to fetch must be an interger between 0 and 100")

        resp = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/messages", bucket=bucket, **params),
        )

        data = await resp.json()

        for message in data:
            msg = Message(**message)
            self.conn.client.INTERNAL_STORAGE['messages'].update({f'{self.id}:{msg.id}': msg})
            yield msg

    @pydantic.validate_arguments
    async def bulk_delete(self, *messages: Union[Message, Snowflake], reason: str = None) -> None:
        """|coro|

        Deletes messages in bulk, in a channel.

        .. warning::
            When deleting in bulk, you need atleast 2 messages and less then 100.
            
            You must also provide your own messages to delete, 
            for a ``purge`` like method, 
            use messages from :meth:`TextChannel.fetch_messages`.

        Parameters
        ----------
        messages: Union[:class:`Message`, :class:`Snowflake`]
            Messages to be deleted
        reason: :class:`str`
            Reason for deleting messages
        """
        headers = dict()
        if reason:
            headers.update({'X-Audit-Log-Reason': reason})

        if 2 < len(messages) < 100:
            raise ValueError('Messages to delete must be greater then 2 and less then 100')

        ids = set(map(lambda x: getattr(x, 'id', x), messages))

        await self.conn.request(
            Route("POST", path=f"/channels/{self.id}/messages/bulk-delete"),
            data={'messages': list(ids)},
            headers=headers
        )

        self.conn.client.loop.create_task(
            _pop_task(self.conn.client, self.id, *ids), 
            name=f"acord: bulk delete: {len(ids)}"
        )

    # Circular imports - Fix typehint when importing
    async def fetch_invites(self) -> List[Any]:
        """|coro|

        Fetches all invites from channel
        """
        from acord.models import Invite

        r = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/invites")
        )
        invites = await r.json()

        return [Invite(**inv) for inv in invites]

    async def create_invite(self, *, reason: str = None, **data) -> Any:
        """|coro|

        Creates new invite in channel

        max_age: :class:`int`
            How long the invite can be used for,
            must be greater or equal to 0
            and less then 604800 (7 Days).

            .. note::
                0 is for never
        max_uses: :class:`int`
            How many times invite can be used,
            before expiring.
            Must be greater or equal to 0
            and less then 100.

            .. note::
                0 is for infinite
        temporary: :class:`bool`
            Whether this invite only grants temporary membership
        unique: :class:`bool`
            If true,
            don't try to reuse a similar invite
            (useful for creating many unique one time use invites)
        """
        from acord.models import Invite

        headers = dict()
        if reason:
            headers.update({'X-Audit-Reason': reason})
        
        if data:
            data = InviteCreatePayload(**data)

        r = await self.conn.request(
            Route("POST", path=f"/channels/{self.id}/invites"),
            data=data,
            headers=headers
        )

        return Invite(**(await r.json()))

    @pydantic.validate_arguments
    async def follow(self, *, channel: Union[Channel, Snowflake]) -> Dict[str, Snowflake]:
        """|coro|

        Follows a guild news channel

        Parameters
        ----------
        channel: Union[:class:`Channel`, :class:`Snowflake`]
            Target channel, 
            or channel to recieve messages from this channel.

        Returns
        -------
        A dictionary with the keys:
        
        * channel_id: source channel id
        * webhook_id: created target webhook id
        """
        if isinstance(channel, Channel):
            channel = channel.id

        r = await self.conn.request(
            Route("POST", path=f'/channels/{self.id}/followers'),
            data={'webhook_channel_id': channel},
        )

        return await r.json()

    async def create_thread(
        self, 
        *, 
        message: Union[Message, Snowflake] = None,
        reason: str = None,
        **options) -> Optional[Thread]:
        """|coro|

        Creates a thread in this channel

        Parameters
        ----------
        message: Union[:class:`Message`, :class:`Snowflake`]
            Message to start thread with
        """
        if message:
            message_id = int(getattr(message, 'id', message))
            path = f'/channels/{self.id}/messages/{message_id}/threads'
        else:
            path = f'/channels/{self.id}/threads'

        data = ThreadCreatePayload(**options)
        headers = dict({"Content-Type": "application/json"})

        if reason:
            headers.update({'X-Audit-Log-Reason': str(reason)})

        r = await self.conn.request(
            Route("POST", path=path),
            headers=headers,
            data=data.json()
        )
        thread = Thread(conn=self.conn, **(await r.json()))
        self.guild.threads.update({thread.id: thread})

        return thread

    async def fetch_active_threads(self) -> Iterator[Thread]:
        """|coro|

        Fetches all active threads in channel

        .. warning::

            .. rubric:: Depreciated

            This method will no longer work when using API Version >= 10,
            instead implement :meth:`Guild.fetch_active_threads`
        """
        if int(self.conn.client.gateway_version[1]) >= 10:
            raise APIObjectDepreciated("This method has been dropped,\
                please use `Guild.active_threads`")

        r = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/threads/active")
        )
        body = await r.json()

        for thread in body['threads']:
            tr = Thread(**thread)
            self.guild.threads.update({tr.id: tr})
            yield tr

    async def fetch_public_archived_threads(
        self,
        *,
        before: datetime.datetime = None,
        limit: int = None
        ) -> Iterator[Thread]:
        """|coro|

        Fetches all public archived thread in channel
        """
        body = dict()
        if before:
            body.update(before=before.isoformat())
        if limit:
            body.update(limit=int(limit))

        r = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/threads/archived/public"),
            data=body
        )
        data = await r.json()

        for thread in data['threads']:
            tr = Thread(**thread)
            self.guild.threads.update({tr.id: tr})
            yield tr

    async def fetch_private_archived_threads(
        self,
        *,
        before: datetime.datetime = None,
        limit: int = None
        ) -> Iterator[Thread]:
        """|coro|

        Fetches all private archived thread in channel
        """
        body = dict()
        if before:
            body.update(before=before.isoformat())
        if limit:
            body.update(limit=int(limit))

        r = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/threads/archived/private"),
            data=body
        )
        data = await r.json()

        for thread in data['threads']:
            tr = Thread(**thread)
            self.guild.threads.update({tr.id: tr})
            yield tr

    async def fetch_joined_private_archived_threads(
        self,
        *,
        before: datetime.datetime = None,
        limit: int = None
        ) -> Iterator[Thread]:
        """|coro|

        Fetches all private archived threads,
        that the client has joined
        """
        body = dict()
        if before:
            body.update(before=before.isoformat())
        if limit:
            body.update(limit=int(limit))

        r = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/users/@me/threads/archived/private"),
            data=body
        )
        data = await r.json()

        for thread in data['threads']:
            tr = Thread(**thread)
            self.guild.threads.update({tr.id: tr})
            yield tr

    @property
    def guild(self):
        """ Returns the guild were channel was created in """
        guild = self.conn.client.get_guild(self.guild_id)
        
        if not guild:
            raise ValueError('Target guild can no longer be found')
        return guild
