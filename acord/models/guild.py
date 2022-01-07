from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Union
from enum import Enum
from io import BytesIO
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
    VoiceRegion,
    Integration,
    Invite,
    GuildTemplate,
    Snowflake,
)

from acord.utils import _d_to_channel, _payload_dict_to_json
from acord.payloads import (
    ChannelCreatePayload,
    GuildCreatePayload, 
    RoleCreatePayload,
    RoleMovePayload,
    GuildTemplateCreatePayload,
    TemplateCreatePayload,
)
from acord.bases import (
    GuildMessageNotification,
    ExplicitContentFilterLevel,
    MFALevel,
    NSFWLevel,
    PremiumTierLevel,
    VerificationLevel,
)
from acord.webhooks.main import Webhook


GUILD_TEXT = [ChannelTypes.GUILD_TEXT, ChannelTypes.GUILD_NEWS]


class Ban(pydantic.BaseModel):
    reason: str
    user: User


class GuildWidget(pydantic.BaseModel):
    enabled: bool
    channel_id: Snowflake


class GuildWidgetImageStyle(Enum):
    shield = "shield"
    banner1 = "banner1"
    banner2 = "banner2"
    banner3 = "banner3"
    banner4 = "banner4"


class WelcomeChannel(pydantic.BaseModel):
    channel_id: Snowflake
    description: str
    emoji_id: Optional[Snowflake]
    emoji_name: str


class WelcomeScreen(pydantic.BaseModel):
    description: str
    welcome_channels: List[Any]


class Guild(pydantic.BaseModel, Hashable):
    """Respresentation of a discord guild

    .. note::
        When working with the guild object,
        :attr:`Guild.large` may be useful to prevent grabbing members which exist but are not cached.
        This is only application when this value is ``True``.
    """
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
    """ Default message notification """

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
    """required MFA level for the guild"""

    nsfw: bool
    """ Whether the guild is marked as NSFW """
    nsfw_level: NSFWLevel
    """Guild NSFW level"""

    owner_id: Snowflake
    """ ID of the guild owner """

    preferred_locale: str
    """ the preferred locale of a Community guild """
    premium_progress_bar_enabled: Optional[bool]
    """ Whether Boosts progress bar is enabled """
    premium_subscription_count: int
    """ Number of guild boosts """
    premium_tier: PremiumTierLevel
    """ premium tier (Server Boost level) """
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
    """ verification level required for the guild """

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

    def get_member(self, member_id: Snowflake, /) -> Optional[Member]:
        """|func|

        Gets a member from internal mapping

        Parameters
        ----------
        member_id: :class:`Snowflake`
            ID of member to get
        """
        return self.members.get(member_id)

    def get_channel(self, channel_id: Snowflake, /) -> Optional[Channel]:
        """|func|

        Gets a channel from cache,
        which only belongs to this guild

        Parameters
        ----------
        channel_id: :class:`Snowflake`
            ID of channel to get
        """
        channel = self.conn.INTERNAL_STORAGE["channels"].get(channel_id)
        if channel:
            # check if channel guild id == self.id
            # if not return
            if not getattr(channel, "guild_id", 0) == self.id:
                # if ID doesnt exists, "dm channels", set to 0 so can be compared
                return
            return channel

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

        Returns an iterator of voice region objects for the guild.
        """
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/regions")
        )

        for region in (await r.json()):
            yield VoiceRegion(**region)

    async def fetch_integrations(self) -> Iterator[Integration]:
        """|coro|

        Returns an iterator of integrations in the guild
        """
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/integrations")
        )

        for integration in (await r.json()):
            yield Integration(guild_id=self.id, **integration)

    async def fetch_widget_settings(self) -> GuildWidget:
        """|coro|

        Returns the guild widget settings
        """
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/widget")
        )

        return GuildWidget(**(await r.json()))

    async def fetch_widget(self) -> Dict[str, Any]:
        """|coro|

        Fetches guild widget,
        returns the raw data as of now
        """
        # TODO: Wait for docs of `/widget.json` to be updated
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/widget.json")
        )

        return (await r.json())

    async def fetch_vanity_invite(self) -> Invite:
        """|coro|

        Fetches guild vanity invite
        """
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/vanity-url")
        )
        data = await r.json()

        self.vanity_url_code = data["code"]

        return Invite(
            code=data["code"],
            channel=None,
            guild=self
        )

    async def fetch_guild_widget_image(
        self, 
        *, 
        style: GuildWidgetImageStyle = GuildWidgetImageStyle.shield
    ) -> BytesIO:
        """|coro|

        Fetches guild widget image, 
        using one of :class:`GuildWidgetImageStyle`.
        Returns :obj:`py:io.BytesIO` with the image in it.

        Parameters
        ----------
        style: :class:`GuildWidgetImageStyle`
            Style of banner
        """
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/widget.png", style=style)
        )

        io = BytesIO(await r.read())
        io.seek(0)

        return io

    async def fetch_welcome_screen(self) -> WelcomeScreen:
        """|coro|

        Fetches guild welcome screen
        """
        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/welcome-screen")
        )

        return WelcomeScreen(**(await r.json()))

    async def fetch_webhooks(self) -> Iterator[Webhook]:
        """|coro|

        Fetches all webhooks in guild
        """
        bucket = dict(guild_id=self.id)

        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/webhooks", bucket=bucket)
        )

        for hook in (await r.json()):
            yield Webhook(adapter=self.conn._session, **hook)

    async def fetch_template(self, code: str, /) -> GuildTemplate:
        """|coro|

        Fetches a guild template

        Parameters
        ----------
        code: :class:`str`
            template code to fetch
        """
        bucket = dict(guild_id=self.id)

        r = await self.conn.request(
            Route("GET", path=f"/guilds/templates/{code}", bucket=bucket)
        )

        return GuildTemplate(conn=self.conn, **(await r.json()))

    async def fetch_templates(self) -> Iterator[GuildTemplate]:
        """|coro|

        Fetches all templates in the guild
        """
        bucket = dict(guild_id=self.id)

        r = await self.conn.request(
            Route("GET", path=f"/guilds/{self.id}/templates", bucket=bucket)
        )

        for template in (await r.json()):
            yield GuildTemplate(conn=self.conn, **template)

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

    async def edit_widget(self, *, reason: str = None, **data) -> GuildWidget:
        """|coro|

        Edits guild widget

        Parameters
        ----------
        enabled: :class:`bool`
            whether the widget is enabled
        channel_id: :class:`Snowflake`
            the widget channel id
        """
        data = GuildWidget(**data)

        headers = dict({"Content-Type": "application/json"})

        if reason:
            headers.update({'X-Audit-Log-Reason': reason})

        r = await self.conn.request(
            Route("PATH", path=f"/guilds/{self.id}/widget"),
            headers=headers
        )

        return GuildWidget(**(await r.json()))

    @pydantic.validate_arguments
    async def edit_welcome_screen(
        self, *,
        enabled: bool,
        welcome_channels: List[WelcomeChannel],
        description: str,
        reason: str
    ) -> WelcomeScreen:
        """|coro|

        Modifies guild welcome screen

        Parameters
        ----------
        enabled: :class:`bool`
            whether screen is enabled or not
        welcome_channels: List[:class:`WelcomeChannel`]
            channels linked in the welcome screen and their display options
        description: :class:`str`
            the server description to show in the welcome screen
        reason: :class:`str`
            Reason for modifying guild welcome screen
        """
        headers = dict({"Content-Type": "application/json"})

        if reason:
            headers.update({"X-Audit-Log-Reason": reason})

        data = {
            "enabled": enabled,
            "welcome_channels": [i.dict() for i in welcome_channels],
            "description": description
        }

        r = await self.conn.request(
            Route("PATCH", path=f"/guilds/{self.id}/welcome-screen"),
            headers=headers,
            data=json.dumps(data)
        )

        return WelcomeScreen(**(await r.json()))

    async def create_template(self, **data) -> GuildTemplate:
        """|coro|

        Create new guild template

        Parameters
        ----------
        name: :class:`str`
            name of template
        description: :class:`str`
            description of template
        """
        payload = TemplateCreatePayload(**data)

        r = await self.conn.request(
            Route("POST", path=f"/guilds/{self.id}/templates"),
            data=payload.json(),
            headers={"Content-Type": "application/json"}
        )

        return GuildTemplate(conn=self.conn, **(await r.json()))

    @classmethod
    async def create(cls, client, **data) -> Optional[Guild]:
        """|coro|

        Creates a new guild,
        were the client is the owner.

        .. warning::
            Can only be used for bots in less then **10** guilds

        Parameters
        ----------
        client: :class:`Client`
            client being used to create guild
        name: :class:`str`
            name of the guild (2-100 characters)
        icon: :class:`File`
            image for the guild icon
        verification_level: :class:`VerificationLevel`
            verification level for guild
        default_message_notifications: :class:`GuildMessageNotification`
            default message notif for guild
        explicit_content_filter: :class:`ExplicitContentFilterLevel`
            explicit content filter for guild
        roles: List[:class:`Role`]
            list of roles for guild
        channels: List[:class:`PartialChannel`]
            list of partial channels for guild
        afk_channel_id: :class:`Snowflake`
            id for afk channel
        afk_timeout: :class:`int`
            afk timeout in seconds
        system_channel_id: :class:`Snowflake`
            the id of the channel where guild notices such as welcome messages and boost events are posted
        system_channel_flags: :class:`SystemChannelFlags`
            guild system channel flags
        """
        payload = GuildCreatePayload(**data)

        r = await client.http.request(
            Route("POST", path="/guilds"),
            headers={"Content-Type": "application/json"},
            data=payload.json()
        )

        return cls(**(await r.json()))

    @classmethod
    async def create_from_template(cls, client, code: str, **data) -> Guild:
        """|coro|

        Creates a guild from a template

        .. warning::
            Can only be used for bots in less then **10** guilds

        Parameters
        ----------
        client: :class:`Client`
            client being used to create guild
        code: :class:`str`
            Template code to create guild from
        name: :class:`str` *
            Name of guild
        icon: :class:`File`
            Icon for guild
        """
        payload = GuildTemplateCreatePayload(**data)

        r = await client.http.request(
            Route("POST", path=f"/guilds/templates/{code}"),
            data=payload.json(),
            headers={"Content-Type": "application/json"}
        )

        return Guild(conn=client.http, **(await r.json()))

    async def delete(self) -> None:
        """|coro|

        Deletes this guild permanently,
        client must be owner 
        """
        await self.conn.request(Route("DELETE", path=f"/guilds/{self.id}"))
