from __future__ import annotations
from typing import Optional
import pydantic
import re
from aiohttp import ClientSession

from acord.models import Snowflake, User
from acord.core.abc import buildURL
from .types import WebhookType
from .methods import WebhookMethods

url_pattern = re.compile(
    "(?P<scheme>https?):\/\/(?P<domain>(?:ptb\.|canary\.)?discord(?:app)?\.com)\/api(?:\/)?(?P<api_version>v\d{1,2})?\/webhooks\/(?P<webhook_identifier>\d{17,19})\/(?P<webhook_token>[\w-]{68})"
)


class Webhook(WebhookMethods, pydantic.BaseModel):
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
    avatar: str
    """ the default user avatar hash of the webhook """
    token: Optional[str]
    """ the secure token of the webhook (returned for Incoming Webhooks) """
    application_id: Snowflake
    """ the bot/OAuth2 application that created this webhook """
    url: Optional[str]
    """ the url used for executing the webhook """

    @classmethod
    async def from_id(cls, id: Snowflake):
        async with ClientSession() as client:
            async with client.request("GET", buildURL(f"webhooks/{id}")) as r:
                return cls(**(await r.json()))

    @classmethod
    async def from_token(cls, id: Snowflake, token: str):
        async with ClientSession() as client:
            async with client.request("GET", buildURL(f"webhooks/{id}/{token}")) as r:
                return cls(**(await r.json()))


class PartialWebhook(WebhookMethods):
    id: Snowflake
    """ ID of webhook """
    token: str
    """ Webhook token """

    def __init__(self, adapter=None, *, url: str = None, **data):
        if url is not None:
            url_match = url_pattern.match(url)

            assert url_match is not None

            id, token = url_match.group("webhook_identifier"), url_match.group(
                "webhook_token"
            )
            data.update(id=id, token=token)

        data.update(adapter=adapter)

        super().__init__(**data)
