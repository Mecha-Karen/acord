from __future__ import annotations
from typing import Optional
import pydantic
import re

from acord.models import (
    Snowflake,
    User
)
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


class PartialWebhook(WebhookMethods, pydantic.BaseModel):
    id: Snowflake
    token: str

    def __init__(self, *, url: str = None, **data):
        if url:
            assert url_pattern.match(url) is not None

            id, token = (url.split('/'))[:-2]

        super().__init__(**data)
