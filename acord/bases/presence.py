from __future__ import annotations

from enum import Enum, IntEnum
from typing import List, Optional
import pydantic
import time


class StatusType(str, Enum):
    online = "online"
    dnd = "dnd"
    idle = "idle"
    invisible = "invisible"
    offline = "offline"


class ActivityType(IntEnum):
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


class Activity(pydantic.BaseModel):
    name: str
    type: int
    url: Optional[str]


class Presence(pydantic.BaseModel):
    activities: List[Activity]
    status: StatusType
    afk: Optional[bool] = False
    since: Optional[float]

    @pydantic.validator("since", pre=True)
    def _validate_since(cls, _, **kwargs) -> int:
        idle = kwargs["values"]["status"] == StatusType.idle

        if not idle:
            return None

        if _:
            return _
        return (time.time() * 1000)


def game(name: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(activities=[Activity(
        name=name,
        type=ActivityType.GAME,
    )], status=status)


def listening(name: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(activities=[Activity(
        name=name,
        type=ActivityType.LISTENING,
    )], status=status)


def watching(name: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(activities=[Activity(
        name=name,
        type=ActivityType.WATCHING,
    )], status=status)


def competing(name: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(activities=[Activity(
        name=name,
        type=ActivityType.COMPETING,
    )], status=status)


def streaming(name: str, url: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(activities=[Activity(
        name=name,
        type=ActivityType.STREAMING,
        url=url
    )], status=status)
