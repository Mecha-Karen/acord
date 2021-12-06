from typing import Optional, Literal, Union, List, Dict, Any
import pydantic

from acord.bases import File, Embed, AllowedMentions
from .models import Message, MessageReference, Snowflake


class ChannelEditPayload(pydantic.BaseModel):
    name: Optional[str]
    type: Optional[Literal[0, 5]]
    position: Optional[int]
    topic: Optional[str]
    nsfw: Optional[bool]
    ratelimit: Optional[int]
    permission_overwrites: Optional[List[Any]]
    category: Optional[int]
    archive_duration: Optional[Literal[0, 60, 1440, 4230, 10080]]
    reason: Optional[str]


class MessageCreatePayload(pydantic.BaseModel):
    allowed_mentions: Optional[AllowedMentions]
    content: Optional[str]
    embeds: Optional[Union[List[Embed], Embed]]
    files: Optional[Union[List[File], File]]
    message_reference: Optional[Union[Message, Snowflake, Dict, MessageReference]]
    tts: Optional[bool] = False

    @pydantic.validator('content')
    def _validate_content(cls, content: str) -> str:
        if len(content) > 2000:
            raise ValueError('Message content cannot be greater then 2000')
        return content

    @pydantic.validator('files')
    def _validate_file(cls, files) -> list:    
        if isinstance(files, File):
            return [files]
        
        assert all(
            (isinstance(i, File) and getattr(i, 'is_closed', None) is False) 
            for i in files
            ), "Invalid list of files passed through"
        
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
