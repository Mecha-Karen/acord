from typing import Optional, Literal, Union, List, Dict, Any
import pydantic

from acord.bases import (
    File, 
    Embed, 
    AllowedMentions, 
    PermissionsOverwrite, 
    MessageFlags
)
from .models import Message, MessageReference, Snowflake


class ChannelEditPayload(pydantic.BaseModel):
    name: Optional[str]
    type: Optional[Literal[0, 5]]
    position: Optional[int]
    topic: Optional[str]
    nsfw: Optional[bool]
    ratelimit: Optional[int]
    permission_overwrites: Optional[Union[List[PermissionsOverwrite], PermissionsOverwrite]]
    category: Optional[int]
    archive_duration: Optional[Literal[0, 60, 1440, 4230, 10080]]
    reason: Optional[str]

    @pydantic.validator('permission_overwrites')
    def _validate_perms(cls, val) -> list:
        if isinstance(val, list):
            return val
        return [val]


class MessageCreatePayload(pydantic.BaseModel):
    allowed_mentions: Optional[AllowedMentions]
    content: Optional[str]
    embeds: Optional[Union[List[Embed], Embed]] = list()
    files: Optional[Union[List[File], File]] = list()
    message_reference: Optional[Union[Message, Snowflake, Dict, MessageReference]]
    tts: Optional[bool] = False
    # Hold off for later releases
    # components: List[Dict[str, Any]]

    @pydantic.validator('content')
    def _validate_content(cls, content: str) -> str:
        if len(content) > 2000:
            raise ValueError('Message content cannot be greater then 2000')
        return content

    @pydantic.validator('files')
    def _validate_file(cls, files) -> list:    
        if isinstance(files, File):
            files = [files]
        
        assert all(
            (isinstance(i, File) and getattr(i, 'is_closed', None) is False) 
            for i in files
            ), "Invalid list of files, make sure they are not closed and are file objects"
        
        return files

    @pydantic.validator('message_reference')
    def _validate_mr(cls, ref) -> int:
        if isinstance(ref, int):
            return MessageReference(message_id=ref)
        if isinstance(ref, Message):
            return MessageReference(message_id=ref.id, 
                                    guild_id=ref.guild_id, 
                                    channel_id=ref.channel_id
                                    )
        if isinstance(ref, dict):
            return MessageReference(**ref)
        return ref

    @pydantic.validator('embeds')
    def _validate_embeds(cls, embeds) -> list:
        if isinstance(embeds, list):
            return embeds
        return [embeds]


class MessageEditPayload(pydantic.BaseModel):
    content: Optional[str]
    embeds: Optional[str]
    flags: Optional[MessageFlags]
    allowed_mentions: Optional[AllowedMentions]
    # Hold off for later releases
    # components: List[Dict[str, Any]]
    files: Optional[List[File]]

    @pydantic.validator('content')
    def _validate_content(cls, content: str) -> str:
        if len(content) > 2000:
            raise ValueError('Message content cannot be greater then 2000')
        return content

    @pydantic.validator('files')
    def _validate_file(cls, files) -> list:    
        if isinstance(files, File):
            files = [files]
        
        assert all(
            (isinstance(i, File) and getattr(i, 'is_closed', None) is False) 
            for i in files
            ), "Invalid list of files, make sure they are not closed and are file objects"
        
        return files


class InviteCreatePayload(pydantic.BaseModel):
    target_type: Optional[Literal[1, 2]]
    target_user_id: Optional[int]
    target_application_id: Optional[int]

    max_age: int = 86400
    max_uses: int = 0
    temporary: bool = False
    unique: bool = False

    @pydantic.validator("max_age")
    def _validate_max_age(cls, age) -> int:
        assert 0 <= age <= 604800, "Max age of invite must be 0 - 604800"
        return age

    @pydantic.validator("max_uses")
    def _validate_max_uses(cls, uses) -> int:
        assert 0 <= uses <= 100, "Max uses of invite must be 0 - 100"
        return uses


class ThreadCreatePayload(pydantic.BaseModel):
    name: str
    type: Literal[10, 11, 12] = 11
    auto_archive_duration: Optional[Literal[0, 60, 1440, 4320, 10080]] = 60
    invitable: Optional[bool] = False
    rate_limit_per_user: Optional[int]

    @pydantic.validator("name")
    def _validate_name(cls, name) -> str:
        assert 0 < len(name) <= 100, "Name of thread must be greater then 0 but less then 100"
        return name

    @pydantic.validator("rate_limit_per_user")
    def _validate_slowmode(cls, sm) -> int:
        assert 0 <= sm <= 21600, "Slowmode cannot be greater then 21600 and less then 0"
        return sm


class ThreadEditPayload(pydantic.BaseModel):
    name: Optional[str]
    archived: Optional[bool]
    auto_archive_duration: Optional[Literal[0, 60, 1440, 4320, 10080]]
    rate_limit_per_user: Optional[int]

    @pydantic.validator("name")
    def _validate_name(cls, name) -> str:
        assert 0 < len(name) <= 100, "Name of thread must be greater then 0 but less then 100"
        return name

    @pydantic.validator("rate_limit_per_user")
    def _validate_slowmode(cls, sm) -> int:
        assert 0 <= sm <= 21600, "Slowmode cannot be greater then 21600 and less then 0"
        return sm
