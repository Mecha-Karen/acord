from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Union
import pydantic
import datetime
import json

from acord.core.abc import DISCORD_EPOCH, Route
from acord.bases import Hashable, ChannelTypes
from acord.models import (
    Channel,
    TextChannel,
    Thread,
    Emoji,
    Role,
    Member,
    User,
    Sticker,
    Snowflake,
)

from acord.bases import (
    GuildMessageNotification,
    ExplicitContentFilterLevel,
    MFALevel,
    NSFWLevel,
    PremiumTierLevel,
    VerificationLevel,
    VoiceRegion,
)
from acord.utils import _d_to_channel, _payload_dict_to_json
from acord.payloads import (
    ChannelCreatePayload, 
    RoleCreatePayload,
    RoleMovePayload,
)


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

    channels: Dict[Snowflake, Channel]
    """ All channels in the guild """
    default_message_notifications: GuildMessageNotification
    """ Default message notification

    :class:`GuildMessageNotification`
    """

    description: Optional[str]
    """ the description of a Community guild """
    discovery_splash: Optional[str]

    embedded_activities: List[Any]

    emojis: Dict[Snowflake, Emoji]
    """ List of emojis in guild """
    explicit_content_filter: ExplicitContentFilterLevel
    """explicit content filter level

    :class:`ExplicitContentFilterLevel`
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

    mfa_level: MFALevel
    """required MFA level for the guild

    :class:`MFALevel`
    """

    nsfw: bool
    """ Whether the guild is marked as NSFW """
    nsfw_level: NSFWLevel
    """Guild NSFW level

    :class:`NSFWLevel`
    """

    owner_id: Snowflake
    """ ID of the guild owner """

    preferred_locale: str
    """ the preferred locale of a Community guild """
    premium_progress_bar_enabled: Optional[bool]
    """ Whether Boosts progress bar is enabled """
    premium_subscription_count: int
    """ Number of guild boosts """
    premium_tier: PremiumTierLevel
    """ premium tier (Server Boost level)

    :class:`PremiumTierLevel`
    """
    presences: Optional[List[Dict[str, Any]]]
    """ presences of the members in the guild, will only include non-offline members if the size is greater than large threshold """
    public_updates_channel_id: Optional[Snowflake]
    """ the id of the channel where admins and moderators of Community guilds receive notices from Discord """

    roles: Dict[Snowflake, Role]
    """ List of roles in the guild """
    rules_channel_id: Optional[Snowflake]
    """ the id of the channel where Community guilds can display rules and/or guidelines """

    splash: Optional[str]
    """ URL of the guild splash """
    stage_instances: Optional[List[Any]] = list()
    """ Stage instances in the guild """
    stickers: Optional[Dict[Snowflake, Sticker]] = dict()
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

    verification_level: VerificationLevel
    """ verification level required for the guild

    :class:`VerificationLevel`
    """

    voice_states: Optional[List[Any]] = list()
    """ array of partial voice state objects """

    created_at: Optional[datetime.datetime]
    """ when the guild was created """

    @pydantic.validator("members", pre=True)
    def _validate_members(cls, members, **kwargs) -> Dict[Snowflake, Member]:
        conn = kwargs["values"]["conn"]
        id = kwargs["values"]["id"]

        return {
            int(m["user"]["id"]): Member(conn=conn, guild_id=id, **m) for m in members
        }

    @pydantic.validator("threads", pre=True)
    def _validate_threads(cls, threads, **kwargs) -> Dict[Snowflake, Thread]:
        conn = kwargs["values"]["conn"]

        return {int(t["id"]): Thread(conn=conn, **t) for t in threads}

    @pydantic.validator("roles", pre=True)
    def _validate_roles(cls, roles, **kwargs) -> Dict[Snowflake, Role]:
        conn = kwargs["values"]["conn"]
        id = kwargs["values"]["id"]

        return {int(r["id"]): Role(conn=conn, guild_id=id, **r) for r in roles}

    @pydantic.validator("emojis", pre=True)
    def _validate_emojis(cls, emojis, **kwargs) -> Dict[Snowflake, Emoji]:
        conn = kwargs["values"]["conn"]
        id = kwargs["values"]["id"]

        return {int(e["id"]): Emoji(conn=conn, guild_id=id, **e) for e in emojis}

    @pydantic.validator("stickers", pre=True)
    def _validate_stickers(cls, stickers, **kwargs) -> Dict[Snowflake, Sticker]:
        conn = kwargs["values"]["conn"]

        return {int(s["id"]): Sticker(conn=conn, **s) for s in stickers}

    """ End of list -> mapping """

    @pydantic.validator("icon")
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

    @pydantic.validator("channels", pre=True)
    def _validate_guild_channels(
        cls, channels: list, **kwargs
    ) -> List[Union[TextChannel, Any]]:
        mapping = dict()
        conn = kwargs["values"]["conn"]
        id = kwargs["values"]["id"]

        for channel in channels:
            channel.update({"guild_id": id})
            ch, _ = _d_to_channel(channel, conn)

            conn.client.INTERNAL_STORAGE["channels"].update({ch.id: ch})
            mapping.update({ch.id: ch})

        return mapping

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

        id = kwargs["values"]["id"]
        return f"https://cdn.discordapp.com/splashes/{id}/{splash}.png"

    @pydantic.validator("created_at")
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
        r = await self.conn.request(
            Route(
                "GET", path=f"/guilds/{self.id}/channels", bucket=dict(guild_id=self.id)
            )
        )
        channels = await r.json()

        for channel in channels:
            ch, _ = _d_to_channel(channel, self.conn)
            yield ch

    async def fetch_active_threads(
        self, *, include_private: bool = True
    ) -> Iterator[Thread]:
        """|coro|

        Fetches all active threads in guild

        Parameters
        ----------
        include_private: :class:`bool`
            Whether to include private threads when yielding
        """
        r = await self.conn.request(
            Route(
                "GET",
                path=f"/guilds/{self.id}/threads/active",
                bucket=dict(guild_id=self.id),
            )
        )
        body = await r.json()

        for thread in body["threads"]:
            if (
                thread["type"] == ChannelTypes.GUILD_PRIVATE_THREAD
                and not include_private
            ):
                continue
            tr = Thread(conn=self.conn, **thread)

            self.threads.update({tr.id: tr})
            yield tr

    async def fetch_member(
        self, *, member: Union[Member, Snowflake]
    ) -> Optional[Member]:
        """|coro|

        Fetches a member from the guild

        Parameters
        ----------
        member: Union[:class:`Member`, :class:`Snowflake`]
            Member to fetch
        """
        r = await self.conn.request(
            Route(
                "GET",
                path=f"/guilds/{self.id}/members/{member}",
                bucket=dict(guild_id=self.id),
            )
        )
        fetched_member = Member(conn=self.conn, **(await r.json()))
        self.members.update({fetched_member.id: fetched_member})
        return fetched_member

    async def fetch_members(
        self, *, limit: int = 1, after: Snowflake = 0
    ) -> Iterator[Member]:
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
            "GET", path=f"/guilds/{self.id}/members", limit=int(limit), after=int(after)
        )
        r = await self.conn.request(route)
        members = await r.json()

        for member in members:
            fmember = Member(conn=self.conn, **member)
            self.members.update({fmember.id: fmember})
            yield fmember

    async def fetch_members_by_name(
        self, query: str, *, limit: int = 1
    ) -> Iterator[Member]:
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
            limit=int(limit),
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
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/bans", bucket=dict(guild_id=self.id))
        )
        for ban in await r.json():
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
        user_id = getattr(user_id, "id", user_id)

        r = await self.conn.request(
            Route(
                "GET",
                path=f"/guilds/{self.id}/bans/{user_id}",
                bucket=dict(guild_id=self.id),
            )
        )
        return Ban(**(await r.json()))

    async def fetch_roles(self) -> Iterator[Role]:
        """|coro|

        Fetches roles in guild
        """
        r = await self.conn.request(Route("GET", path=f"/guilds/{self.id}/roles"))

        for role in (await r.json()):
            r = Role(guild_id=self.id, **role)
            self.roles.update({r.id: r})
            yield r

    @pydantic.validate_arguments
    async def fetch_prune_count(self, *, days: int = 7, include_roles: List[Role] = list()) -> int:
        """|coro|

        Fetches guild prune count and returns the count,
        without actually pruning members.

        Parameters
        ----------
        days: :class:`int`
            number of days to count prune for (1-30)
        include_roles: List[:class:`Role`]
            role(s) to include
        """
        assert 0 < days <= 30, "Number of days must be between 1 and 30"

        roles = ",".join([i.id for i in include_roles])

        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/prune", days=days, include_roles=roles)
        )

        return (await r.json())['pruned']

    async def fetch_regions(self) -> Iterator[VoiceRegion]:
        """|coro|

        Returns a list of voice region objects for the guild.
        """
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/regions")
        )

        for region in (await r.json()):
            yield VoiceRegion(**region)


    async def unban(
        self, user_id: Union[User, Snowflake], *, reason: str = None
    ) -> None:
        """|coro|

        Removes ban from user

        Parameters
        ----------
        user_id: Union[:class:`User`, :class:`Snowflake`]
            user ID to be unbanned
        """
        user_id = getattr(user_id, "id", user_id)
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        await self.conn.request(
            Route("DELETE", path=f"/guilds/{self.id}/bans/{user_id}"), headers=headers
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
        reason: str = None,
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
        roles = [getattr(i, "id", i) for i in roles]
        user_id = getattr(user_id, "id", user_id)
        data = dict(
            access_token=access_token, nick=nick, roles=roles, mute=mute, deaf=deaf
        )
        data = {k: v for k, v in data.keys() if v is not None}
        route = Route(
            "PUT",
            path=f"/guilds/{self.id}/members/{user_id}",
            bucket=dict(guild_id=self.id),
        )

        headers = {"Content-Type": "application/json"}

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        r = await self.conn.request(route, data=data, headers=headers)

        if r.status == 201:
            member = Member(conn=self.conn, **(await r.json()))
            self.members.update({member.id: member})
        else:
            member = self.members.get(user_id)
        return member

    async def create_channel(self, *, reason: str = None, **data) -> Channel:
        """|coro|

        Creates a new channel in the guild

        Parameters
        ----------
        name: :class:`str`
            Name of channel
        type: :class:`ChannelTypes`
            Type of channel to create
        topic: :class:`str`
            Channel topic
        bitrate: :class:`int`
            Bitrate for channel, **VOICE ONLY**
        user_limit: :class:`int`
            User limit for channel, **VOICE ONLY**
        rate_limit_per_user: :class:`int`
            Slowmode for channel
        position: :class:`integer`
            Sorting position of channel
        permission_overwrite: List[:class:`PermissionsOverwrite`]
            channel permission overwrites
        parent_id: :class:`Snowflake`
            id of the parent category for channel
        nsfw: :class:`bool`
            Whether to mark channel as NSFW
        reason: :class:`str`
            Reason for creating channel
        """
        payload = ChannelCreatePayload(**data)
        headers = dict({"Content-Type": "application/json"})

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        r = await self.conn.request(
            Route("POST", path=f"/guilds/{self.id}/channels"),
            data=payload.json(),
            headers=headers,
        )

        channel, _ = _d_to_channel((await r.json()), self.conn)

        self.conn.client.INTERNAL_STORAGE["channels"].update({channel.id: channel})
        self.channels.update({channel.id: channel})

        return channel

    async def create_role(self, *, reason: str = None, **data) -> Role:
        """|coro|

        Creates a new role in the guild

        Parameters
        ----------
        name: :class:`str`
            Name of new role,
            if not provided sets to ``new role``
        permissions: :class:`Permissions`
            Role permissions
        color: :class:`Color`
            Colour of role, 
            for reference checkout :attr:`Embed.color`
        hoist: :class:`bool`
            Whether to dispay role seperatley
        icon: :class:`File`
            the role's icon image
        unicode_emoji: :class:`str`
            the role's icon as a unicode emoji
        mentionable: :class:`bool`
            whether the role can be mentioned
        reason: :class:`str`
            reason for creating role
        """
        data = _payload_dict_to_json(RoleCreatePayload, **data)
        headers = dict({'Content-Type': 'application/json'})

        if reason:
            headers.update({'X-Audit-Log-Reason': reason})

        r = await self.conn.request(
            Route("POST", path=f"/guilds/{self.id}/roles"),
            data=data,
            headers=headers
        )

        role = Role(conn=self.conn, **(await r.json()))
        self.roles.update({role.id: role})

        return role

    @pydantic.validate_arguments
    async def move_roles(self, *positons: RoleMovePayload, reason: str = None) -> Iterator[Role]:
        """|coro|

        Modify positon of roles in guild

        Parameters
        ----------
        *positions: :class:`RoleMovePayload`
            Arguments of role move payloads,
            or dict with keys:

            * id: :class:`Snowflake`
            * position: :class:`int`

            Were id is the role ID and position is its new position 
        """
        payload = json.dumps([i.dict() for i in positons])
        headers = dict({"Content-Type": "application/json"})

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        r = await self.conn.request(
            Route("PATCH", path=f"/guilds/{self.id}/roles"),
            data=payload,
            headers=headers
        )

        for role in (await r.json()):
            role_ = Role(guild_id=self.id, **role)
            self.roles.update({role_.id: role_})

            yield role_

    @pydantic.validate_arguments
    async def prune(
        self,
        *,
        days: int = 7,
        compute_prune_count: bool = True,
        include_roles: List[Role] = list(),
        reason: str = None
    ) -> Optional[int]:
        """|coro|

        Prunes members,
        returns amount of pruned IF
        ``compute_prune_count`` is True.

        Parameters
        ----------
        days: :class:`int`
            number of days to count prune for (1-30)
        compute_prune_count: :class:`bool`
            whether to return amount of members pruned,
            for larger guilds it is discouraged to use this.
        include_roles: List[:class:`Role`]
            role(s) to include
        reason: :class:`str`
            Reason for starting prune
        """
        assert 0 < days <= 30, "Number of days must be between 1 and 30"

        roles = ",".join([i.id for i in include_roles])
        headers = dict()

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        r = await self.conn.request(
            Route("POST", 
                path=f"/guilds/{self.id}/prune", 
                days=days, include_roles=roles,
                compute_prune_count=str(compute_prune_count).lower()
                ),
            headers=headers
        )

        return (await r.json())['pruned']
