import asyncio
from typing import Any, AsyncGenerator, Callable, Dict, List, Literal, Optional, Tuple, Union, overload
from acord.bases import _C

from acord import (
    User, 
    Presence, 
    Snowflake, 
    Stage, 
    StagePrivacyLevel,
    Guild,
    UDAppCommand, 
    ApplicationCommand,
    VoiceConnection,
    Message,
    Channel
)

class Client(object):
    INTERNAL_STORAGE: Dict[str, Any]
    loop: asyncio.AbstractEventLoop
    token: Optional[str]
    encoding: Literal["JSON", "ETF"]
    compress: Optional[bool]
    _events: Dict[str, _C]
    session_id: Optional[str]
    gateway_version: Optional[Union[str, int]]
    user: Optional[User]
    awaiting_voice_connections: Dict[str, str]
    voice_connections: Dict[int, VoiceConnection]
    acked_at: float
    latency: float

    # Properties and what not
    guilds: List[Guild]

    # Methods
    @overload
    def bind_token(self, token: str) -> None: ...
    @overload
    def on(self, name: str) -> Callable[[Callable[..., Any]], Any]: ...
    @overload
    def on(self, name: str, *, once: bool) -> Callable[[Callable[..., Any]], Any]: ...
    @overload
    def on_error(self, event_method: Any) -> None: ...
    @overload
    def dispatch(self, event_name: str) -> None: ...
    @overload
    def dispatch(self, event_name: str, *args) -> None: ...
    @overload
    def dispatch(self, event_name: str, *args, **kwargs) -> None: ...
    @overload
    async def resume(self) -> None: ...
    @overload
    def wait_for(self, event: str) -> _C: ...
    @overload
    async def wait_for(self, event: str) -> Tuple[Any]: ...
    @overload
    def wait_for(self, event: str, *, check: Callable[..., bool]) -> _C: ...
    @overload
    async def wait_for(
        self, event: str, *, check: Callable[..., bool]
    ) -> Tuple[Any]: ...
    @overload
    def wait_for(
        self, event: str, *, check: Callable[..., bool], timeout: int
    ) -> _C: ...
    @overload
    async def wait_for(
        self, event: str, *, check: Callable[..., bool], timeout: int
    ) -> Tuple[Any]: ...
    @overload
    def wait_for(self, event: str, *, timeout: int) -> _C: ...
    @overload
    async def wait_for(self, event: str, *, timeout: int) -> Tuple[Any]: ...
    @overload
    async def change_presence(self, presence: Presence) -> None: ...
    @overload
    async def update_voice_state(
        self,
        *,
        guild_id: Snowflake,
        channel_id: Snowflake,
        self_mute: bool,
        self_deaf: bool,
    ) -> None: ...
    @overload
    async def update_voice_state(self, **data) -> None: ...
    @overload
    async def create_stage_instance(
        self, *, channel_id: Snowflake, topic: str
    ) -> Stage: ...
    @overload
    async def create_stage_instance(
        self,
        *,
        channel_id: Snowflake,
        topic: str,
        privacy_level: StagePrivacyLevel,
        reason: str,
    ) -> Stage: ...
    @overload
    def register_application_command(
        self,
        command: UDAppCommand
    ) -> None: ...
    @overload
    def register_application_command(
        self,
        command: UDAppCommand,
        *,
        guild_ids: Union[List[int], None] = None,
        extend: bool = True,
    ) -> None: ...
    @overload
    async def create_application_command(
        command: UDAppCommand
    ) -> Union[ApplicationCommand, List[ApplicationCommand]]: ...
    @overload
    async def create_application_command(
        self,
        command: UDAppCommand,
        *,
        guild_ids: Union[List[int], None] = None,
        extend: bool = True,
    ) -> Union[ApplicationCommand, List[ApplicationCommand]]: ...
    @overload
    async def bulk_update_global_app_commands(self, commands: List[UDAppCommand]) -> None: ...
    @overload
    async def bulk_update_guild_app_commands(
        self,
        guild_id: Snowflake,
        commands: List[UDAppCommand],
    ) -> None: ...
    @overload
    async def disconnect(self): ...
    @overload
    def get_message(self, channel_id: int, message_id: int) -> Optional[Message]: ...
    @overload
    def get_user(self, user_id: int) -> Optional[User]: ...
    @overload
    def get_guild(self, guild_id: int) -> Optional[Guild]: ...
    @overload
    def get_channel(self, channel_id: int) -> Optional[Channel]: ...
    @overload
    async def fetch_user(self, user_id: int) -> Optional[User]: ...
    @overload
    async def fetch_channel(self, channel_id: int) -> Optional[Channel]: ...
    @overload
    async def fetch_message(
        self, channel_id: int, message_id: int
    ) -> Optional[Message]: ...
    @overload
    async def fetch_guild(self, guild_id: int) -> Optional[Guild]: ...
    @overload
    async def fetch_guild(
        self, guild_id: int, *, with_counts: bool = False
    ) -> Optional[Guild]: ...
    @overload
    async def fetch_glob_app_commands(self) -> AsyncGenerator[ApplicationCommand, None]: ...
    @overload
    async def fetch_glob_app_command(self, command_id: Snowflake) -> ApplicationCommand: ...
    @overload
    async def gof_channel(self, channel_id: int) -> Optional[Channel]: ...
    @overload
    def run(self, token: str) -> None: ...
    @overload
    def run(self, token: str, *, reconnect: bool, resumed: bool) -> None: ...
