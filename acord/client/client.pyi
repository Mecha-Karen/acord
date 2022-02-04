import asyncio
from re import A, S
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union, overload
from acord.bases import _C

from acord import User, Presence, Snowflake, Stage, StagePrivacyLevel, Guild

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

    # Properties and what not
    guilds: List[Guild]
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
    def run(self, token: str) -> None: ...
    @overload
    def run(self, token: str, *, reconnect: bool, resumed: bool) -> None: ...
