from __future__ import annotations

import pydantic
import datetime

from acord.bases import Hashable, File
from acord.models import User
from acord.errors import APIObjectDepreciated

from acord.core.signals import gateway
from asyncio import get_event_loop

from typing import Any, List, Optional, Type, Union


class Message(pydantic.BaseModel, Hashable):
    conn: Any                                 # Connection Object - For internal use

    activity: Any                             # sent with Rich Presence-related chat embeds TODO: Message Activity
    application: Any                          # sent with Rich Presence-related chat embeds TODO: Application Object
    attachments: List[Any]                    # List of file objects TODO: Asset object
    author: User                              # User object of who sent the message
    channel_id: int                           # id of the channel were the message was send
    components: List[Any]                     # List of buttons, selects etc..
    content: str                              # Message content
    edited_timestamp: Optional[
        Union[bool, datetime.datetime]        # If not false contains timestamp of edited message
    ]
    embeds: List[Any]                         # List of embeds TODO: Embed object  
    flags: int                                # Message flags
    id: int                                   # Message ID
    interaction: Optional[Any]                # Message interactin TODO: Interaction object
    guild_id: Optional[int]                   # Guild of were message was sent
    member: Optional[Any]                     # Member object of who sent the message TODO: Member object
    mentions: List[Union[User, Any]]          # List of mentioned users
    mention_everyone: bool                    # Message mentioned @everyone
    mention_roles: List[Any]                  # Message mentioned any roles
    mention_channels: Optional[List[Any]]     # List of mentioned channels TODO: Channel Object
    nonce: Optional[int]                      # Message nonce: used for verifying if message was sent
    pinned: bool                              # Message pinned in channel or not
    reactions: Optional[List[Any]]            # List of reactions TODO: reaction object
    referenced_message: Optional[
        Union[Message, Any]                   # Message replied to TODO: partial message
    ]
    thread: Optional[Any]                     # Channel thread TODO: Channel Thread Object
    timestamp: datetime.datetime              # Timestamp of when message was sent
    tts: bool                                 # Is a text to speech message
    type: int                                 # Message type, e.g. DEFAULT, REPLY
    sticker_items: Optional[List[Any]]        # List of stickers TODO: Sticker object
    stickers: Optional[List[Any]]             # Depreciated raises error if provided 
    webhook_id: Optional[int]                 # Webhook message ID

    class Config:
        arbitrary_types_allowed = True

    @pydantic.validator('timestamp')
    def _timestamp_validator(cls, timestamp):
        try:
            return datetime.datetime.fromisoformat(timestamp)
        except TypeError:
            if isinstance(timestamp, datetime.datetime):
                return timestamp
            raise

    @pydantic.validator('stickers')
    def _stickers_depr_error(cls, _):
        raise APIObjectDepreciated('"stickers" attribute has been dropped, please use "sticker_items"')

    @pydantic.validator('author')
    def _validate_author(cls, data: User, **kwargs):
        data = data.dict()
        conn = kwargs['values']['conn']

        data['conn'] = conn

        return User(**data)

    def __init__(self, **data):

        super().__init__(**data)
