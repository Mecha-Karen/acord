from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union
import pydantic
import datetime

from acord.core.abc import DISCORD_EPOCH
from acord.bases import Hashable, ChannelTypes
from acord.models import Snowflake

from .channels.text import TextChannel
from .emoji import Emoji
from .roles import Role

class Guild(pydantic.BaseModel, Hashable):
    conn: Any  # Connection object - For internal use

    id: Snowflake
    """ Guild ID """
    name: str
    """ Name of guild """
    icon: Optional[str]
    """ Guild icon """

    afk_channel_id: Optional[Snowflake]
    """ AFK channel id """
    afk_timeout: Optional[int]
    """ AFK timeout duration """

    application_command_count: Optional[int]
    application_command_counts: Optional[Dict[str, int]]

    application_id: Optional[Snowflake]
    """ application id of the guild creator if it is bot-created """
    banner: Optional[str]
    """ URL for the guild banner """

    channels: List[Any]  # This gets sorted out with validators
    """ All channels in the guild """
    default_message_notifications: Literal[0, 1]
    """ Default message notification

    * 0 - ALL_MESSAGES (members will receive notifications for all messages by default)
    * 1 - ONLY_MENTIONS (members will receive notifications only for messages that @mention them by default)
    """

    description: Optional[str]
    """ the description of a Community guild """
    discovery_splash: Optional[str]

    embedded_activities: List[Any]

    emojis: List[Emoji]
    """ List of emojis in guild """
    explicit_content_filter: int
    """explicit content filter level

    * 0 - DISABLED (media content will not be scanned)
    * 1 - MEMBERS_WITHOUT_ROLE (media content sent by members without roles will be scanned)
    * 2 - ALL_MEMBERS (media content sent by all members will be scanned)
    """

    features: List[str]
    """ List of guild features """

    guild_hashes: Dict[Any, Any]

    guild_scheduled_events: List[Dict[str, Any]]
    """ List of scheduled guild events """  # TODO: events object

    hub_type: Optional[bool]

    joined_at: datetime.datetime
    """ When the user joined this guild """

    large: bool
    """ Whether this guild is considered as large """

    lazy: Optional[bool]

    max_members: int
    """ Maximum amount of members allowed to join this guild """

    max_video_channel_users: Optional[int]
    """ The maximum amount of users in a video channel """

    member_count: int
    """ Amount of members in this guild """

    members: List[Any]
    """ List of all members in the guild """  # TODO: member object

    mfa_level: int
    """required MFA level for the guild

    * 0 - NONE (guild has no MFA/2FA requirement for moderation actions)
    * 1 - ELEVATED (guild has a 2FA requirement for moderation actions)
    """

    nsfw: bool
    """ Whether the guild is marked as NSFW """
    nsfw_level: int
    """Guild NSFW level

    * DEFAULT - 0
    * EXPLICIT - 1
    * SAFE - 2
    * AGE_RESTRICTED - 3
    """

    owner_id: Snowflake
    """ ID of the guild owner """

    preferred_locale: str
    """ the preferred locale of a Community guild """
    premium_progress_bar_enabled: Optional[bool]
    """ Whether Boosts progress bar is enabled """
    premium_subscription_count: int
    """ Number of guild boosts """
    premium_tier: int
    """ premium tier (Server Boost level)

    * NONE	 - 0	guild has not unlocked any Server Boost perks
    * TIER_1 - 1	guild has unlocked Server Boost level 1 perks
    * TIER_2 - 2	guild has unlocked Server Boost level 2 perks
    * TIER_3 - 3	guild has unlocked Server Boost level 3 perks
    """
    presences: Optional[List[Dict[str, Any]]]
    """ presences of the members in the guild, will only include non-offline members if the size is greater than large threshold """
    public_updates_channel_id: Optional[Snowflake]
    """ the id of the channel where admins and moderators of Community guilds receive notices from Discord """

    roles: List[Role]
    """ List of roles in the guild """
    rules_channel_id: Optional[Snowflake]
    """ the id of the channel where Community guilds can display rules and/or guidelines """

    splash: Optional[str]
    """ URL of the guild splash """
    stage_instances: Optional[List[Any]] = list()
    """ Stage instances in the guild """
    stickers: Optional[List[Any]] = list()
    """ List of guild stickers """
    system_channel_flags: Optional[int]
    """ system channel flags """
    system_channel_id: Optional[Snowflake]
    """ the id of the channel where guild notices such as welcome messages and boost events are posted """

    threads: Optional[List[Any]] = list()
    """ List of threads in the guild """

    unavailable: Optional[bool]
    """ Whether guild is operational or lost due to outage """

    vanity_url_code: Optional[str]
    """ the vanity url code for the guild """

    verification_level: int
    """ verification level required for the guild

    * NONE	    - 0	(unrestricted)
    * LOW	    - 1	(must have verified email on account)
    * MEDIUM	- 2	(must be registered on Discord for longer than 5 minutes)
    * HIGH	    - 3	(must be a member of the server for longer than 10 minutes)
    * VERY_HIGH	- 4	(must have a verified phone number )
    """

    voice_states: Optional[List[Any]] = list()
    """ array of partial voice state objects """

    created_at: Optional[datetime.datetime]
    """ when the guild was created """

    @pydantic.validator('icon')
    def _validate_guild_icon(cls, icon: str, **kwargs) -> Optional[str]:
        if not icon:
            return None

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/icons/{id}/{icon}.png"

    @pydantic.validator("banner")
    def _validate_guild_banner(cls, banner: str, **kwargs) -> Optional[str]:
        if not banner:
            return None

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/banners/{id}/{banner}.png"

    @pydantic.validator("channels")
    def _validate_guild_channels(
        cls, channels: list, **kwargs
    ) -> List[Union[TextChannel, Any]]:
        new_channels = list()
        conn = kwargs["values"]["conn"]
        id = kwargs["values"]["id"]

        for channel in channels:
            if channel["type"] == ChannelTypes.GUILD_TEXT:
                new_channels.append(TextChannel(conn=conn, guild_id=id, **channel))
            else:
                new_channels.append(channel)

            cid = int(channel["id"])

            conn.client.INTERNAL_STORAGE["channels"].update({cid: new_channels[-1]})

        return new_channels

    @pydantic.validator("discovery_splash")
    def _validate_guild_dsplash(cls, discovery_splash: str, **kwargs) -> Optional[str]:
        if not discovery_splash:
            return None

        id = kwargs["values"]["id"]
        return (
            f"https://cdn.discordapp.com/discovery-splashes/{id}/{discovery_splash}.png"
        )

    @pydantic.validator("splash")
    def _validate_guild_spash(cls, splash: str, **kwargs) -> Optional[str]:
        if not splash:
            return None
        
        id = kwargs['values']['id']
        return f'https://cdn.discordapp.com/splashes/{id}/{splash}.png'

    @pydantic.validator('created_at')
    def _validate_guild_created_at(cls, _, **kwargs) -> datetime.datetime:
        timestamp = ((kwargs["values"]["id"] >> 22) + DISCORD_EPOCH) / 1000
        return datetime.datetime.fromtimestamp(timestamp)
