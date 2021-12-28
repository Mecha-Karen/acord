from __future__ import annotations
from typing import Optional
import pydantic
import re
from aiohttp import ClientSession

from acord.models import (
    Snowflake,
    User
)
from acord.core.abc import buildURL
from .types import WebhookType
from .methods import WebhookMethods

url_pattern = re.compile("^https:\/\/discord.com\/api\/webhooks\/[0-9]+\/[a-zA-Z0-9_]*$")


class Webhook(WebhookMethods, pydantic.BaseModel):
    id: Snowflake
    type: WebhookType
    guild_id: Optional[Snowflake]
    channel_id: Snowflake
    user: Optional[User]
    name: str
    avatar: str
    token: Optional[str]
    application_id: Snowflake
    url: Optional[str]

    @classmethod
    async def from_id(cls, id: Snowflake):
        async with ClientSession() as client:
            async with client.request(
                "GET", buildURL(f"webhooks/{id}")
            ) as r:
                return cls(**(await r.json()))

    @classmethod
    async def from_token(cls, id: Snowflake, token: str):
        async with ClientSession() as client:
            async with client.request(
                "GET", buildURL(f"webhooks/{id}/{token}")
            ) as r:
                return cls(**(await r.json()))

class PartialWebhook(WebhookMethods):
    id: Snowflake
    token: str

    def __init__(self, adapter = None, *, url: str = None, **data):
        if url is not None:
            assert url_pattern.match(url) is not None

            id, token = (url.split('/'))[-2:]
            data.update(id=id, token=token)

        data.update(adapter=adapter)

        super().__init__(**data)
