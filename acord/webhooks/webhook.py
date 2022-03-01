from __future__ import annotations
from typing import Any, Optional

import pydantic
import re
from aiohttp import ClientSession, FormData

from acord.models import (
    Snowflake, User, WebhookMessage
)
from acord.bases import Hashable
from acord.payloads import WebhookMessageCreate, WebhookEditPayload
from acord.core.abc import Route, buildURL

from .connection import WebhookConnection
from .types import WebhookType

url_pattern = re.compile(
    "(?P<scheme>https?):\/\/(?P<domain>(?:ptb\.|canary\.)?discord(?:app)?\.com)\/api(?:\/)?(?P<api_version>v\d{1,2})?\/webhooks\/(?P<webhook_identifier>\d{17,19})\/(?P<webhook_token>[\w-]{68})"
)


class Webhook(Hashable, pydantic.BaseModel):
    """Representation of a discord webhook
    
    This class can simply be used for sending simple messages,
    and editing and deleting them.
    Only **IF** you stick to the default session.

    If you pass your client through the args,
    or overwrite :attr:`Webhook.conn` with :attr:`Client.http._session`.
    Your able to properly interact with the generated message object.
    """
    conn: Any

    id: Snowflake
    """ the id of the webhook """
    type: WebhookType
    """ the type of the webhook """
    guild_id: Optional[Snowflake]
    """ the guild id this webhook is for, if any """
    channel_id: Snowflake
    """ the channel id this webhook is for, if any """
    user: Optional[User]
    """ the user this webhook was created by (not returned when getting a webhook with its token) """
    name: str
    """ the default name of the webhook """
    avatar: Optional[pydantic.AnyHttpUrl]
    """ the default user avatar hash of the webhook """
    token: Optional[str]
    """ the secure token of the webhook (returned for Incoming Webhooks) """
    application_id: Optional[Snowflake]
    """ the bot/OAuth2 application that created this webhook """
    url: Optional[str]
    """ the url used for executing the webhook """

    def __init__(self, **kwds) -> None:
        conn = kwds.pop("conn", None)

        if conn is None:
            loop = kwds.pop("loop", None)
            client = kwds.pop("client", None)
            session = kwds.pop("session", None)

            _kwds = {"loop": loop, "client": client, "session": session}
            _kwds = {k: v for k, v in _kwds.items() if v is not None}

            conn = WebhookConnection(**_kwds)

        kwds["conn"] = conn

        super().__init__(**kwds)

    ## NOTE: Methods
    # Methods are all sync but return coros which can be awaited

    async def fetch_message(
        self, 
        message_id: Snowflake, 
        *, 
        thread_id: Snowflake = None
    ) -> WebhookMessage:
        """|coro|

        Fetches a message sent by the webhook

        Parameters
        ----------
        message_id: :class:`Snowflake`
            ID of message to fetch
        thread_id: :class:`Snowflake`
            ID of thread message is in
        """
        route = Route(
            "GET",
            path=f"webhooks/{self.id}/{self.token}/messages/{message_id}",
            thread_id=thread_id
        )

        r = await self.conn.request(route)

        return WebhookMessage(
            conn=self.conn,
            token=self.token,
            webhook_id=self.id,
            **(await r.json())
        )

    async def execute(
        self,
        *,
        wait: bool = False,
        thread_id: Snowflake = None,
        **kwds
    ) -> Optional[WebhookMessage]:
        """|coro|

        Executes a webhook.

        .. note::
            This function accepts all parameters from :class:`TextChannel.send`,
            as a well a few extras which are documented below.

        Parameters
        ----------
        wait: :class:`bool`
            Whether to wait for message created to be returned
        thread_id: :class:`Snowflake`
            ID of the thread to send message in
        username: :class:`str`
            Username to override default username
        avatar_url: :class:`str`
            **URL** of avatar to override default avatar
        """
        payload = WebhookMessageCreate(**kwds)

        if not any(
            i
            for i in payload.dict()
            if i in ["content", "files", "embeds", "sticker_ids"]
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

        route = Route(
            "POST",
            path=f"/webhooks/{self.id}/{self.token}",
            thread_id=thread_id,
            wait=str(wait).lower()  # True -> true
        )

        r = await self.conn.request(route, data=form_data)

        if wait:
            return WebhookMessage(
                conn=self.conn,
                token=self.token,
                webhook_id=self.id,
                **(await r.json())
            )

    async def edit(
        self, *, reason: str = None, with_token: bool = True, auth: str = None, **kwds
    ) -> Webhook:
        """|coro|

        Edits webhook.

        Parameters
        ----------
        name: :class:`str`
            New name of webhook,
            still cannot be called ``clyde``
        avatar: :class:`File`
            New avatar for webhook
        channel_id: :class:`Snowflake`
            New channel to move webhook to
        reason: :class:`str`
            reason for editing webhook
        with_token: :class:`bool`
            Whether to modify with token or not,
            defaults to ``True``
        auth: :class:`str`
            If not with_token,
            auth is your **BOT TOKEN**,
            which will be used to make request
        """
        payload = WebhookEditPayload(**kwds)
        headers = dict({"Content-Type": "application/json"})

        if auth:
            headers.update({"Authorization": auth})

        if reason:
            headers.update({"X-Audit-Log-Reason": headers})

        tk = ""
        if with_token:
            tk = self.token

        r = await self.conn.request(
            Route("POST", path=f"/webhooks/{self.id}/{tk}"),
            headers=headers,
            data=payload.json()
        )

        return Webhook(
            conn=self.conn,
            **(await r.json())
        )

    async def delete(
        self, *, reason: str = None, with_token: bool = True, auth: str = None
    ) -> None:
        """|coro|

        Deletes webhook

        Parameters
        ----------
        reason: :class:`str`
            reason for deleting webhook
        with_token: :class:`bool`
            Whether to delete with token or not,
            defaults to ``True``
        auth: :class:`str`
            If not with_token,
            auth is your **BOT TOKEN**,
            which will be used to make request
        """
        headers = dict({"Content-Type": "application/json"})

        if auth:
            headers.update({"Authorization": auth})

        if reason:
            headers.update({"X-Audit-Log-Reason": headers})

        tk = ""
        if with_token:
            tk = self.token

        await self.conn.request(
            Route("DELETE", path=f"/webhooks/{self.id}/{tk}"),
            headers=headers
        )

    ## NOTE: Any overwrites

    def dict(self, **kwds) -> dict:
        d = super(Webhook, self).dict(**kwds)

        d.pop("conn")

        return d

    ## NOTE: Class methods

    @classmethod
    async def from_id(cls, id: Snowflake, session: ClientSession = None):
        session = session or ClientSession()

        async with session as client:
            async with client.request("GET", buildURL(f"webhooks/{id}")) as r:
                return cls(**(await r.json()))

    @classmethod
    async def from_token(cls, id: Snowflake, token: str, session: ClientSession = None):
        session = session or ClientSession()

        async with session as client:
            async with client.request("GET", buildURL(f"webhooks/{id}/{token}")) as r:
                return cls(**(await r.json()))

    @classmethod
    async def from_url(cls, url: str):
        url_match = url_pattern.match(url)

        assert url_pattern, "Invalid Webhook URL passed"

        id, token = url_match.group("webhook_identifier"), url_match.group(
            "webhook_token"
        )

        return await cls.from_token(id, token)

    ## DUNDERS

    async def __aenter__(self) -> Webhook:
        return self

    async def __aexit__(self, *_) -> None:
        return
