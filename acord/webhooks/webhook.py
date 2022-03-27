from __future__ import annotations
from typing import Any, List, Optional

import pydantic
import re
from aiohttp import ClientSession
from acord.bases.enums.interactions import InteractionCallback

from acord.models import (
    Snowflake,
    User,
    WebhookMessage,
)
from acord.bases import Hashable, Modal
from acord.payloads import (
    MessageEditPayload,
    WebhookMessageCreate,
    WebhookEditPayload,
    InteractionMessageCreate,
    FormPartHelper,
)
from acord.ext.application_commands import AutoCompleteChoice
from acord.core.abc import Route, buildURL
from acord.utils import message_multipart_helper

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
    or overwrite :attr:`Webhook.conn` with :attr:`Client.http`.
    Your able to properly interact with the generated message object.

    .. note::
        When dealing with interactions,
        it is recommended to use the webhook class,
        instead of :class:`Interaction`
    """

    conn: Any

    id: Snowflake
    """ the id of the webhook """
    type: WebhookType
    """ the type of the webhook """
    guild_id: Optional[Snowflake]
    """ the guild id this webhook is for, if any """
    channel_id: Optional[Snowflake]
    """ the channel id this webhook is for, if any """
    user: Optional[User]
    """ the user this webhook was created by (not returned when getting a webhook with its token) """
    name: str = None
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

    ## NOTE: Default Methods

    async def fetch_message(
        self,
        message_id: Snowflake,
        *,
        thread_id: Snowflake = None,
        use_application_id: bool = False,
    ) -> WebhookMessage:
        """|coro|

        Fetches a message sent by the webhook

        Parameters
        ----------
        message_id: :class:`Snowflake`
            ID of message to fetch
        thread_id: :class:`Snowflake`
            ID of thread message is in
        use_application_id: :class:`bool`
            Whether to use the application id instead of the webhook id
            when fetching message
        """
        id = self.application_id if use_application_id else self.id

        route = Route(
            "GET",
            path=f"webhooks/{id}/{self.token}/messages/{message_id}",
            thread_id=thread_id,
        )

        r = await self.conn.request(route)
        return WebhookMessage(conn=self.conn, webhook=self, **(await r.json()))

    async def delete_message(
        self,
        message_id: Snowflake,
        *,
        thread_id: Snowflake = None,
        reason: str = None,
        use_application_id: bool = False,
    ) -> None:
        """|coro|

        Deletes a message sent by webhook

        Parameters
        ----------
        message_id: :class:`Snowflake`
            ID of message to delete
        thread_id: :class:`Snowflake`
            ID of thread message was sent in
        reason: :class:`str`
            Reason for deleting message
        use_application_id: :class:`bool`
            Whether to use application ID instead of webhook ID
        """
        headers = dict()
        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        id = self.application_id if use_application_id else self.id

        await self.conn.request(
            Route(
                "DELETE",
                f"/webhooks/{id}/{self.token}/messages/{message_id}",
                thread_id=thread_id,
            ),
            headers=headers,
        )

    async def edit_message(
        self,
        message_id: Snowflake,
        *,
        thread_id: Snowflake = None,
        use_application_id: bool = False,
        **kwds,
    ) -> WebhookMessage:
        """|coro|

        Edits a previously sent message from this webhook

        .. note::
            This function accepts all parameters from :class:`Message.edit`,
            as a well a few extras which are documented below.

        Parameters
        ----------
        message_id: :class:`Snowflake`
            ID of message to edit
        thread_id: :class:`Snowflake`
            ID of thread message was sent in
        use_application_id: :class:`bool`
            Whether to use the application ID instead of the Webhook ID
        """
        form_data = message_multipart_helper(MessageEditPayload, {"files"}, **kwds)
        id = self.application_id if use_application_id else self.id

        route = Route(
            "PATCH",
            path=f"/webhooks/{id}/{self.token}/messages/{message_id}",
            thread_id=thread_id,
        )
        r = await self.conn.request(route, data=form_data)

        return WebhookMessage(conn=self.conn, webhook=self, **(await r.json()))

    async def execute(
        self, *, wait: bool = False, thread_id: Snowflake = None, **kwds
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
        form_data = message_multipart_helper(WebhookMessageCreate, {"files"}, **kwds)

        route = Route(
            "POST",
            path=f"/webhooks/{self.id}/{self.token}",
            thread_id=thread_id,
            wait=str(wait).lower(),  # True -> true
        )

        r = await self.conn.request(route, data=form_data)

        if wait:
            return WebhookMessage(conn=self.conn, webhook=self, **(await r.json()))

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
            data=payload.json(),
        )

        return Webhook(conn=self.conn, **(await r.json()))

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
            Route("DELETE", path=f"/webhooks/{self.id}/{tk}"), headers=headers
        )

    ## NOTE: For interactions

    async def respond_with_message(self, **kwds) -> None:
        """|coro|

        Responds to an interaction using a regular message

        .. DANGER::
            This method should only be if :attr:`Webhook.type` is ``3``.
            As it will fail for any other type of webhook.

        .. note::
            All parameters from :meth:`TextChannel.send` are valid,
            additional parameters documented below

        Parameters
        ----------
        flags: :class:`IMessageFlags`
            Flags for message
        ack: :class:`bool`
            Whether to ack the response,
            giving the client ``15`` mins to edit to this response.
        """
        if kwds.pop("ack", False):
            d_type = InteractionCallback.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        else:
            d_type = InteractionCallback.CHANNEL_MESSAGE_WITH_SOURCE

        route = Route("POST", path=f"/interactions/{self.id}/{self.token}/callback")
        form_data = message_multipart_helper(
            FormPartHelper,
            {"data": {"files"}},
            inner_key="data",
            data=InteractionMessageCreate(**kwds),
            type=d_type,
        )

        await self.conn.request(route, data=form_data)

    async def respond_with_modal(self, modal: Modal) -> None:
        """|coro|

        Responds to an interaction using a modal.

        Parameters
        ----------
        modal: :class:`Modal`
            Modal to respond with
        """
        d = FormPartHelper(type=InteractionCallback.MODAL, data=modal)

        await self.conn.request(
            Route("POST", path=f"/interactions/{self.id}/{self.token}/callback"),
            data=d.json(),
            headers={"Content-Type": "application/json"},
        )

    async def respond_to_autocomplete(self, choices: List[AutoCompleteChoice]) -> None:
        """|coro|

        Responds to an interaction with a list of choices

        Parameters
        ----------
        choices: List[:class:`AutoCompleteChoice`]
            List of choices to return the user,
            can be a list of dicts with the mapping name: value
        """
        d = {"choices": choices}

        d = FormPartHelper(
            type=InteractionCallback.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT, data=d
        )

        await self.conn.request(
            Route("POST", path=f"/interactions/{self.id}/{self.token}/callback"),
            data=d.json(),
            headers={"Content-Type": "application/json"},
        )

    async def send_followup_message(self, **kwds) -> None:
        """|coro|

        Sends a followup message to an interaction

        .. note::
            All parameters from :meth:`TextChannel.send` are valid,
            any additional parameters documented below

        Parameters
        ----------
        flags: :class:`IMessageFlags`
            Flags for message
        """

        route = Route("POST", path=f"/webhooks/{self.application_id}/{self.token}")

        form_data = message_multipart_helper(
            InteractionMessageCreate, {"files"}, **kwds
        )

        await self.conn.request(route, data=form_data)

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
