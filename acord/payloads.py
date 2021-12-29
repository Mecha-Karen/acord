from typing import Any, Optional, Literal, Union, List, Dict
import pydantic
import datetime
import imghdr
import base64

from acord.bases import (
    File, 
    Embed,
    Color,
    Permissions,
    AllowedMentions, 
    PermissionsOverwrite, 
    MessageFlags,
    ActionRow,
    VerificationLevel,
    GuildMessageNotification,
    ExplicitContentFilterLevel,
    SystemChannelFlags
    )
from acord.bases.embeds import _rgb_to_hex
from .models import (
    Message, 
    MessageReference, 
    Role, 
    Snowflake, 
    PartialChannel
)


def _file_to_image_data(file):
    format = imghdr.what(file.fp)
    file.reset(seek=True)
    data = base64.b64encode(file.fp.read()).decode("ascii")

    file.close()

    data["avatar"] = f"data:image/{format};base64,{data}"


class GenericWebsocketPayload(pydantic.BaseModel):
    op: int
    d: Any


class ChannelEditPayload(pydantic.BaseModel):
    name: Optional[str]
    type: Optional[Literal[0, 5]]
    position: Optional[int]
    topic: Optional[str]
    nsfw: Optional[bool]
    ratelimit: Optional[int]
    permission_overwrites: Optional[
        Union[List[PermissionsOverwrite], PermissionsOverwrite]
    ]
    category: Optional[int]
    archive_duration: Optional[Literal[0, 60, 1440, 4230, 10080]]
    reason: Optional[str]

    @pydantic.validator("permission_overwrites")
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
    components: Optional[List[ActionRow]]

    @pydantic.validator("content")
    def _validate_content(cls, content: str) -> str:
        if len(content) > 2000:
            raise ValueError("Message content cannot be greater then 2000")
        return content

    @pydantic.validator("files")
    def _validate_file(cls, files) -> list:
        if isinstance(files, File):
            files = [files]

        assert all(
            (isinstance(i, File) and getattr(i, "is_closed", None) is False)
            for i in files
        ), "Invalid list of files, make sure they are not closed and are file objects"

        return files

    @pydantic.validator("message_reference")
    def _validate_mr(cls, ref) -> int:
        if isinstance(ref, int):
            return MessageReference(message_id=ref)
        if isinstance(ref, Message):
            return MessageReference(
                message_id=ref.id, guild_id=ref.guild_id, channel_id=ref.channel_id
            )
        if isinstance(ref, dict):
            return MessageReference(**ref)
        return ref

    @pydantic.validator("embeds")
    def _validate_embeds(cls, embeds) -> list:
        if isinstance(embeds, list):
            return embeds
        return [embeds]

    @pydantic.validator("components")
    def _validate_components(cls, rows):
        if len(rows) > 5:
            raise ValueError('Message cannot contain more then 5 action rows')
        return rows

class MessageEditPayload(pydantic.BaseModel):
    content: Optional[str]
    embeds: Optional[str]
    flags: Optional[MessageFlags]
    allowed_mentions: Optional[AllowedMentions]
    # Hold off for later releases
    # components: List[Dict[str, Any]]
    files: Optional[List[File]]

    @pydantic.validator("content")
    def _validate_content(cls, content: str) -> str:
        if len(content) > 2000:
            raise ValueError("Message content cannot be greater then 2000")
        return content

    @pydantic.validator("files")
    def _validate_file(cls, files) -> list:
        if isinstance(files, File):
            files = [files]

        assert all(
            (isinstance(i, File) and getattr(i, "is_closed", None) is False)
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
        assert (
            0 < len(name) <= 100
        ), "Name of thread must be greater then 0 but less then 100"
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
        assert (
            0 < len(name) <= 100
        ), "Name of thread must be greater then 0 but less then 100"
        return name

    @pydantic.validator("rate_limit_per_user")
    def _validate_slowmode(cls, sm) -> int:
        assert 0 <= sm <= 21600, "Slowmode cannot be greater then 21600 and less then 0"
        return sm


class ChannelCreatePayload(pydantic.BaseModel):
    name: str

    type: Optional[int]
    topic: Optional[str]
    bitrate: Optional[int]
    user_limit: Optional[int]
    rate_limit_per_user: Optional[int]
    position: Optional[int]
    permission_overwrites: Optional[List[PermissionsOverwrite]]
    parent_id: Optional[Snowflake]
    nsfw: Optional[bool]

    @pydantic.validator("name")
    def _validate_name(cls, name) -> str:
        assert (
            0 < len(name) <= 100
        ), "Name of thread must be greater then 0 but less then 100"
        return name

    @pydantic.validator("topic")
    def _validate_topic(cls, topic) -> str:
        assert 0 < len(topic) <= 1024, "Topic must be greater then 0 but less then 1024"

    @pydantic.validator("rate_limit_per_user")
    def _validate_slowmode(cls, sm) -> int:
        assert 0 <= sm <= 21600, "Slowmode cannot be greater then 21600 and less then 0"
        return sm


class MemberEditPayload(pydantic.BaseModel):
    nick: Optional[str]
    roles: Optional[List[Union[Role, Snowflake]]]
    mute: Optional[bool]
    deaf: Optional[bool]
    channel_id: Optional[Snowflake]
    communication_disabled_until: Optional[datetime.datetime]


class RoleCreatePayload(pydantic.BaseModel):
    name: Optional[str]
    permissions: Optional[Permissions]
    color: Optional[Color]
    hoist: Optional[bool]
    icon: Optional[File]
    unicode_emoji: Optional[str]
    mentionable: Optional[bool]

    def dict(self, *args, **kwargs) -> dict:
        # :meta private:
        # Override pydantic to return `Color` as a hex
        data = super(RoleCreatePayload, self).dict(*args, **kwargs)

        if self.color:
            color = int(_rgb_to_hex(self.color.as_rgb_tuple(alpha=False)), 16)
            data["color"] = color
        
        if self.icon:
            data["icon"] = _file_to_image_data(self.icon.fp)
            self.icon.close()

        return data


class RoleMovePayload(pydantic.BaseModel):
    id: Snowflake
    position: int

    @pydantic.validator("id", pre=True)
    def _validate_role(cls, id) -> None:
        if isinstance(id, Role):
            return id.id

        return id


class RoleEditPayload(pydantic.BaseModel):
    name: Optional[str]
    permissions: Optional[Permissions]
    color: Optional[Color]
    hoist: Optional[bool]
    icon: Optional[File]
    unicode_emoji: Optional[str]
    mentionable: Optional[bool]

    def dict(self, *args, **kwargs) -> dict:
        # :meta private:
        # Override pydantic to return `Color` as a hex
        data = super(RoleEditPayload, self).dict(*args, **kwargs)

        if self.color:
            color = int(_rgb_to_hex(self.color.as_rgb_tuple(alpha=False)), 16)
            data["color"] = color
        
        if self.icon:
            data["icon"] = _file_to_image_data(data["icon"])
            self.icon.close()

        return data


class WebhookCreatePayload(pydantic.BaseModel):
    name: str
    avatar: Optional[File]

    @pydantic.validator("name")
    def _validate_name(cls, name: str) -> str:
        assert len(name) <= 80, "Name of webhook must be less then 80 chars"

        if name.lower() != "clyde":
            raise ValueError("Webhooks cannot be named `clyde`")

        return name

    @pydantic.validator("avatar")
    def _validate_av(cls, avatar: File) -> File:
        assert avatar.is_closed() is False, "File must be open"
        return avatar

    def dict(self, **kwargs) -> dict:
        """ :meta private: """
        data = super(WebhookCreatePayload, self).dict(**kwargs)
        avatar: File = data.pop("avatar")

        data["avatar"] = _file_to_image_data(avatar)
        return data


class WebhookEditPayload(pydantic.BaseModel):
    name: Optional[str]
    avatar: Optional[File]
    channel_id: Optional[Snowflake]

    @pydantic.validator("name")
    def _validate_name(cls, name: str) -> str:
        assert len(name) <= 80, "Name of webhook must be less then 80 chars"

        if name.lower() != "clyde":
            raise ValueError("Webhooks cannot be named `clyde`")

        return name

    @pydantic.validator("avatar")
    def _validate_av(cls, avatar: File) -> File:
        assert avatar.is_closed() is False, "File must be open"
        return avatar

    def dict(self, **kwargs) -> dict:
        """ :meta private: """
        data = super(WebhookEditPayload, self).dict(**kwargs)
        avatar: File = data.pop("avatar")

        data["avatar"] = _file_to_image_data(avatar)
        return data


class GuildCreatePayload(pydantic.BaseModel):
    name: str
    icon: Optional[File]
    verification_level: Optional[VerificationLevel]
    default_message_notifications: Optional[GuildMessageNotification]
    explicit_content_filter: Optional[ExplicitContentFilterLevel]
    roles: Optional[List[Role]]
    channels: Optional[List[PartialChannel]]
    afk_channel_id: Optional[Snowflake]
    afk_timeout: Optional[int]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: Optional[SystemChannelFlags]
