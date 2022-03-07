from __future__ import annotations
from typing import Any, List, Optional
import pydantic

from acord.bases import PermissionsOverwrite
from acord.models import Snowflake
from acord.voice.core import VoiceConnection
from acord.errors import VoiceError
from .base import Channel


class VoiceRegion(pydantic.BaseModel):
    id: Snowflake
    name: str
    optimal: bool
    depreciated: bool
    custom: bool


class VoiceChannel(Channel):
    conn: Any

    guild_id: Snowflake
    """ ID of guild were channel is in """
    name: str
    """ Name of channel """
    nsfw: Optional[bool] = False
    """ Whether channel is marked as NSFW """
    position: int
    """ Position of channel """
    permission_overwrites: Optional[List[PermissionsOverwrite]] = list()
    """ Permissions for channel """
    bitrate: int
    """ the bitrate (in bits) of the voice channel """
    user_limit: int
    """ the user limit of the voice channel """
    parent_id: Optional[Snowflake]
    """ ID of category were channel is in """
    rtc_region: Optional[str]
    """ voice region id for the voice channel, automatic when set to null """

    async def join(
        self,
        *,
        self_mute: bool = False, 
        self_deaf: bool = False,
        wait: bool = True
    ) -> VoiceConnection:
        """|coro|

        Joins this voice channel,
        shortcut for :class:`Client.update_voice_state`.

        Parameters
        ----------
        self_mute: :class:`bool`
            Whether to mute client on join
        self_deaf: :class:`bool`
            Whether to deafen client on join,
            doesn't mute unless specified!
        wait: :class:`bool`
            Whether to wait for the :class:`VoiceConnection` to be returned

        Returns
        -------
        Returns a :class:`VoiceConnection` object,
        which can directly be passed into a reciever/player
        """
        shard = self.conn.client.get_shard(self.guild_id)

        assert shard, "Cannot find allocated shard"

        await shard.update_voice_state(
            guild_id=self.guild_id,
            channel_id=self.id,
            self_mute=self_mute,
            self_deaf=self_deaf,
        )

        if not wait:
            return

        return (await self.conn.client.wait_for(
            "voice_server_update",
            check=self._vc_check,
        ))[0]

    def _vc_check(self, vc) -> bool:
        return vc.guild_id == str(self.guild_id)

    async def leave(self) -> None:
        """|coro|

        Leaves voice channel if client is connected,
        shortcut for :class:`Client.update_voice_state`

        Raises
        ------
        :class:`VoiceError`, when client is not connected to current channel
        """
        state = self.conn.client.voice_connections.get(self.guild_id)

        if not state or int(state.channel_id) == self.id:
            raise VoiceError("Client is not connected to any/this channel")

        await self.conn.client.update_voice_state(
            guild_id=self.guild_id, channel_id=None, self_mute=False, self_deaf=False
        )
