from __future__ import annotations

from aiohttp import ClientSession, ClientResponse, FormData
from typing import Any, Optional, Protocol, runtime_checkable
from pydantic import BaseModel

from acord.models import Snowflake, Message
from acord.payloads import MessageCreatePayload
from acord.core.abc import buildURL


@runtime_checkable
class Adapter(Protocol):
    async def request(method: str, data: Any, *args, **kwargs) -> ClientResponse:
        ...

    async def close() -> None:
        ...


class WebhookMethods(BaseModel):
    adapter: Any

    def __init__(self, adapter = None) -> None:
        if not adapter:
            adapter = ClientSession()

        assert isinstance(adapter, Adapter), "Variable adapter must has an async request & close method"

        super().__init__(adapter=adapter)

    async def fetch_message(self, message_id: Snowflake, *, thread_id: Snowflake = None) -> Message:
        """|coro|

        Fetches a webhook message

        Parameters
        ----------
        thread_id: :class:`Snowflake`
            id of the thread the message is in
        """
        PATH = f"webhooks/{self.id}/{self.token}/messages/{message_id}"

        r = await self.adapter.request(
            "GET", buildURL(PATH, thread_id=thread_id)
        )
        r.raise_for_status()

        return Message(**(await r.json()))

    async def execute(self, 
        *, 
        wait: bool = False, 
        thread_id: Snowflake = False,
        **data
    ) -> Optional[Message]:
        """|coro|
        Creates a new message using webhook

        Parameters
        ----------
        wait: :class:`bool`
            waits for server confirmation of message send before response
        thread_id: :class:`Snowflake`
            Send a message to the specified thread within a webhook's channel.

        All other parameters are the same as,
        :meth:`TextChannel.send`
        """
        payload = MessageCreatePayload(**data)

        if not any(
            i for i in payload.dict() if i in ["content", "files", "embeds", "sticker_ids"]
        ):
            raise ValueError(
                "Must provide one of content, file, embeds, sticker_ids inorder to send a message"
            )

        if any(i for i in (payload.embeds or list()) if i.characters() > 6000):
            raise ValueError("Embeds cannot contain more then 6000 characters")

        form_data = FormData()

        if payload.files:
            for index, file in enumerate(payload.files):

                form_data.add_field(
                    name=f"file{index}",
                    value=file.fp,
                    filename=file.filename,
                    content_type="application/octet-stream",
                )

        form_data.add_field(
            name="payload_json",
            value=payload.json(exclude={"files"}),
            content_type="application/json",
        )

        r = await self.adapter.request(
            "POST", 
            buildURL(
                f"/webhooks/{self.id}/{self.token}",
                thread_id=thread_id,
                wait=str(wait).lower()
                ),
            data=form_data,
        )

        r.raise_for_status()

        try:
            return Message(**(await r.json()))
        except Exception:
            # Message created wasn't returned
            # wait param was false
            return

    async def __aenter__(self, *args, **kwargs) -> WebhookMethods:
        return WebhookMethods(*args, **kwargs)

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.adapter.close()
