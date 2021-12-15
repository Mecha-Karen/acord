from __future__ import annotations
from typing import Any, List, Optional
import pydantic
import datetime

from acord.bases import Hashable
from .guild import Guild
from .channels import Channel
from .user import User


class StageInstanceInvite(pydantic.BaseModel, Hashable):
    members: List[Any]
    participant_count: int
    speaker_count: int
    topic: str


class Invite(pydantic.BaseModel, Hashable):
    conn: Any   # Connection object - For internal use

    code: str
    """the invite code (unique ID)"""
    guild: Optional[Guild]
    """the guild this invite is for"""
    channel: Channel
    """the channel this invite is for"""
    inviter: Optional[User]
    """the user who created the invite"""
    target_type: Optional[int]
    """the type of target for this voice channel invite"""
    target_user: Optional[User]
    """the user whose stream to display for this voice channel stream invite"""
    target_application: Optional[Any]
    """the embedded application to open for this voice channel embedded application invite"""
    approximate_presence_count: Optional[int]
    """approximate count of online members"""
    approximate_member_count: Optional[int]
    """approximate count of total members"""
    expires_at: Optional[datetime.datetime]
    """the expiration date of this invite"""
    stage_instance: Optional[StageInstanceInvite]
    """stage instance data if there is a public Stage instance in the Stage channel this invite is for"""
    guild_scheduled_event: Optional[Any]    # TODO: scheduled event object
    """guild scheduled event"""


    @pydantic.validator("guild", pre=True)
    def _validate_guild(cls, partial_guild: dict, **kwargs) -> Optional[Guild]:
        conn =  kwargs['values']['conn']
        guild_id = int(partial_guild['id'])

        return conn.client.get_guild(guild_id)

    
    @pydantic.validator("channel", pre=True)
    def _validate_channel(cls, partial_channel: dict, **kwargs) -> Optional[Channel]:
        conn =  kwargs['values']['conn']
        channel_id = int(partial_channel['id'])
        
        return conn.client.get_channel(channel_id)
