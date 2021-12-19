from __future__ import annotations

from typing import Any, Dict, Iterator, List, Literal, Optional, Union
import pydantic
import datetime

from acord.core.abc import DISCORD_EPOCH, Route
from acord.bases import Hashable, ChannelTypes
from acord.models import (Channel,
    TextChannel, Thread, Emoji, Role, Member, User,
    Snowflake
)
from acord.models.channels.stage import Stage


GUILD_TEXT = [ChannelTypes.GUILD_TEXT, ChannelTypes.GUILD_NEWS]


class Ban(pydantic.BaseModel):
    reason: str
    user: User


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

    members: Dict[Snowflake, Member]
    """ Mapping of all members in guild """ 

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

    threads: Optional[Dict[Snowflake, Thread]] = dict()
    """ Mapping of threads in the guild """

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

    @pydantic.validator("members", pre=True)
    def _validate_members(cls, members, **kwargs) -> Dict[Snowflake, Member]:
        conn = kwargs['values']['conn']

        return {int(m['user']['id']): Member(conn=conn, **m) for m in members}

    @pydantic.validator("threads", pre=True)
    def _validate_threads(cls, threads, **kwargs) -> Dict[Snowflake, Thread]:
        conn = kwargs['values']['conn']

        return {int(t['id']): Thread(conn=conn, **t) for t in threads}

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

    def get_member(self, member_id: Snowflake) -> Optional[Member]:
        """|func|

        Gets a member from internal mapping

        Parameters
        ----------
        member_id: :class:`Snowflake`
            ID of member to get
        """
        return self.members.get(member_id)

    async def fetch_channels(self) -> Iterator[Channel]:
        """|coro|

        Fetches all channels in the guild,
        doesn't include threads!
        """
        r = await self.conn.request(Route(
            "GET", 
            path=f"/guilds/{self.id}/channels", 
            bucket=dict(guild_id=self.id)
        ))
        channels = await r.json()

        for channel in channels:
            if channel['type'] in GUILD_TEXT:
                yield TextChannel(conn=self.conn, **channel)
            if channel['type'] == ChannelTypes.GUILD_VOICE:
                # TODO: Guild voice channel
                yield channel
            if channel['type'] == ChannelTypes.GUILD_STAGE_VOICE:
                yield Stage(conn=self.conn, **channel)
            if channel['type'] == ChannelTypes.GUILD_CATEGORY:
                # TODO: Guild category
                yield channel
            
            raise ValueError('Unknown channel type encountered, %s, %s' % (
                channel['type'], hasattr(ChannelTypes, channel['type'])
            ))

    async def fetch_active_threads(self, *, include_private: bool = True) -> Iterator[Thread]:
        """|coro|

        Fetches all active threads in guild

        Parameters
        ----------
        include_private: :class:`bool`
            Whether to include private threads when yielding
        """
        r = await self.conn.request(Route(
            "GET",
            path=f"/guilds/{self.id}/threads/active",
            bucket=dict(guild_id=self.id)
        ))
        body = await r.json()

        for thread in body['threads']:
            if thread['type'] == ChannelTypes.GUILD_PRIVATE_THREAD and not include_private:
                continue
            tr = Thread(conn=self.conn, **thread)

            self.threads.update({tr.id: tr})
            yield tr

    async def fetch_member(self, *, member: Union[Member, Snowflake]) -> Optional[Member]:
        """|coro|

        Fetches a member from the guild

        Parameters
        ----------
        member: Union[:class:`Member`, :class:`Snowflake`]
            Member to fetch
        """
        r = await self.conn.request(Route(
            "GET", 
            path=f"/guilds/{self.id}/members/{member}", 
            bucket=dict(guild_id=self.id)
        ))
        fetched_member = Member(conn=self.conn, **(await r.json()))
        self.members.update({fetched_member.id: fetched_member})
        return fetched_member

    async def fetch_members(self, *, limit: int = 1, after: Snowflake = 0) -> Iterator[Member]:
        """|coro|

        Fetches guild members

        Parameters
        ----------
        limit: :class:`int`
            How many many members to fetch, 
            must be less then 1000 and greater then 1.
            Defaults to **1**!
        after: :class:`Snowflake`
            Fetches users after this user
        """
        assert 0 < limit <= 1000, "Limit must be less then 1000 and greater then 0"

        route = Route(
            "GET", 
            path=f"/guilds/{self.id}/members",
            limit=int(limit),
            after=int(after)
            )
        r = await self.conn.request(route)
        members = await r.json()

        for member in members:
            fmember = Member(conn=self.conn, **member)
            self.members.update({fmember.id: fmember})
            yield fmember

    async def fetch_members_by_name(self, query: str, *, limit: int = 1) -> Iterator[Member]:
        """|coro|

        Fetches members by there username(s) or nickname(s)

        Parameters
        ----------
        query: :class:`str`
            Username/Nickame to use
        limit: :class:`int`
        """
        assert 0 < limit <= 1000, "Limit must be less then 1000 and greater then 0"

        route = Route(
            "GET", 
            path=f"/guilds/{self.id}/members/search",
            query=str(query),
            limit=int(limit)
            )
        r = await self.conn.request(route)
        members = await r.json()

        for member in members:
            fmember = Member(conn=self.conn, **member)
            self.members.update({fmember.id: fmember})
            yield fmember

    async def fetch_bans(self) -> Iterator[Ban]:
        """|coro|

        Returns all the users banned in the guild
        """
        r = await self.conn.request(Route(
            "GET", 
            path=f"/guilds/{self.id}/bans", 
            bucket=dict(guild_id=self.id)
        ))
        for ban in (await r.json()):
            yield Ban(**ban)

    async def fetch_ban(self, user_id: Union[User, Snowflake]) -> Optional[Ban]:
        """|coro|

        Fetches ban for this user,
        if exists.

        Parameters
        ----------
        user_id: Union[:class:`User`, :class:`Snowflake`]
            ID of user who was banned
        """
        user_id = getattr(user_id, 'id', user_id)

        r = await self.conn.request(Route(
            "GET", 
            path=f"/guilds/{self.id}/bans/{user_id}", 
            bucket=dict(guild_id=self.id)
        ))
        return Ban(**(await r.json()))

    async def unban(self, user_id: Union[User, Snowflake], *, reason: str = None) -> None:
        """|coro|

        Removes ban from user

        Parameters
        ----------
        user_id: Union[:class:`User`, :class:`Snowflake`]
            user ID to be unbanned
        """
        user_id = getattr(user_id, 'id', user_id)
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.conn.request(
            Route("DELETE", path=f"/guilds/{self.id}/bans/{user_id}"),
            headers=headers
        )

    @pydantic.validate_arguments
    async def add_member(
        self,
        user_id: Union[User, Snowflake],
        access_token: str,
        *,
        nick: str = None,
        roles: List[Union[Role, Snowflake]] = None,
        mute: bool = None,
        deaf: bool = None,
        reason: str = None
    ) -> Optional[Member]:
        """|coro|

        For bots with an ``access_token`` for a :class:`User`,
        you may use this method for adding the user to this guild.

        .. note::
            Requires ``guilds.join`` scope inorder to add the user

        Parameters
        ----------
        user_id: Union[:class:`User`, :class:`Snowflake`]
            User to add to guild
        access_token: :class:`str`
            Access token to be used
        nick: :class:`str`
            Nickname for user
        roles: List[Union[:class:`Role`, :class:`Snowflake`]]
            List of roles to give user on join
        mute: :class:`bool`
            Whether the user is muted in voice channels
        dead: :class:`bool`
            Whether the user is deafened in voice channels
        reason: :class:`str`
            Reason for adding member to guild
        """
        roles = [getattr(i, 'id', i) for i in roles]
        user_id = getattr(user_id, 'id', user_id)
        data = dict(
            access_token=access_token,
            nick=nick,
            roles=roles,
            mute=mute,
            deaf=deaf
        )
        data = {k: v for k, v in data.keys() if v is not None}
        route = Route(
            "PUT",
            path=f"/guilds/{self.id}/members/{user_id}",
            bucket=dict(guild_id=self.id)
        )

        headers = {"Content-Type": "application/json"}

        if reason:
            headers.update({'X-Audit-Log-Reason': reason})

        r = await self.conn.request(
            route, data=data, headers=headers
        )

        if r.status == 201:
            member = Member(conn=self.conn, **(await r.json()))
            self.members.update({member.id: member})
        else:
            member = self.members.get(user_id)
        return member
