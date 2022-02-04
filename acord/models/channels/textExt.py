# text bases, allows methods to be shared between
# - TextChannel
# - Thread
# Without needing to make files huge
from typing import Optional, Iterator, Union
from aiohttp import FormData
from pydantic import validate_arguments

from acord.models import Message, Snowflake
from acord.payloads import MessageCreatePayload
from acord.core.abc import Route


class ExtendedTextMethods:
    def _get_bucket(self):
        guild_id = getattr(self, "guild_id", None)
        return {"channel_id": self.id, "guild_id": guild_id}

    @validate_arguments
    def get_message(self, message_id: Union[Message, Snowflake]) -> Optional[Message]:
        """|func|

        Returns the message stored in the internal cache, may be outdated

        Parameters
        ----------
        message_id: Union[:class:`Message`, :class:`Snowflake`]
            ID of message to get
        """
        return self.conn.client.get_message(channel_id=self.id, message_id=message_id)

    @validate_arguments
    async def fetch_message(
        self, message_id: Union[Message, Snowflake]
    ) -> Optional[Message]:
        """|coro|

        Fetch a message directly from channel/thread

        Parameters
        ----------
        message_id: Union[:class:`Message`, :class:`Snowflake`]
            ID of the message to fetch
        """
        if isinstance(message_id, Message):
            message_id = message_id.id

        bucket = self._get_bucket()

        resp = await self.conn.request(
            Route(
                "GET", path=f"/channels/{self.id}/messages/{message_id}", bucket=bucket
            )
        )

        message = Message(**(await resp.json()))
        self.conn.client.INTERNAL_STORAGE["messages"].update(
            {f"{self.id}:{message.id}": message}
        )

        return message

    async def send(self, **data) -> Optional[Message]:
        """|coro|

        Create a new message in the channel/thread

        Parameters
        ----------
        content: :class:`str`
            Message content, must be below ``2000`` chars.
        files: *Union[List[:class:`File`], :class:`File`]*
            A file or a list of files to be sent. File must not be closed else an error is raised.
        message_reference: Union[:class:`MessageReference`]
            A message to reply to, client must be able to read messages in the channel/thread.
        tts: :class:`bool`
            Whether this is a TTS message
        embeds: *Union[List[:class:`Embed`], :class:`File`]*
            An embed or a list of embeds to send
        components: List[:class:`ActionRow`]
            A list of action rows to send,
            refer to `me <../guides/components.html>`_ for a more detailed guide.
        """
        ob = MessageCreatePayload(**data)

        if not any(
            i for i in ob.dict() if i in ["content", "files", "embeds", "sticker_ids"]
        ):
            raise ValueError(
                "Must provide one of content, file, embeds, sticker_ids inorder to send a message"
            )

        if any(i for i in (ob.embeds or list()) if i.characters() > 6000):
            raise ValueError("Embeds cannot contain more then 6000 characters")

        bucket = self._get_bucket()
        form_data = FormData()

        if ob.files:
            for index, file in enumerate(ob.files):

                form_data.add_field(
                    name=f"file{index}",
                    value=file.fp,
                    filename=file.filename,
                    content_type="application/octet-stream",
                )

        form_data.add_field(
            name="payload_json",
            value=ob.json(exclude={"files"}),
            content_type="application/json",
        )

        r = await self.conn.request(
            Route("POST", path=f"/channels/{self.id}/messages", bucket=bucket),
            data=form_data,
        )

        n_msg = Message(conn=self.conn, **(await r.json()))
        self.conn.client.INTERNAL_STORAGE["messages"].update(
            {f"{self.id}:{n_msg.id}": n_msg}
        )
        return n_msg

    async def trigger_typing(self) -> None:
        """|coro|

        Creates a typing indicator in this channel/thread.
        """
        bucket = self._get_bucket()
        await self.conn.request(
            Route("POST", path=f"/channels/{self.id}/typing", bucket=bucket)
        )

    async def pins(self) -> Iterator[Message]:
        """|coro|

        Fetches channel/thread pins
        """
        bucket = self._get_bucket()
        r = await self.conn.request(
            Route("GET", path=f"/channels/{self.id}/pins", bucket=bucket)
        )
        messages = await r.json()

        for message in messages:
            msg = Message(**message)
            self.conn.client.INTERNAL_STORAGE["messages"].update(
                {f"{self.id}:{msg.id}": msg}
            )
            yield msg
