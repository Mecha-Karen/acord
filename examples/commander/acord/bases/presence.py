from __future__ import annotations
from ctypes import Union

from enum import Enum, IntEnum
from typing import Any, List, Optional
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
    """ Name of activity, if custom should be set to ``Custom Status`` """
    type: int
    """ Type of activity, consider using :class:`ActivityType` """
    url: Optional[str]
    """ URL of activity, if STREAMING. must be one of ``youtube.com`` or ``twitch.tv`` """
    emoji: Optional[Any]
    """ A :class:`PartialEmoji` """
    state: Optional[str]
    """ Should be the value for :attr:`Activity.name` if type is :attr:`ActivityType.CUSTOM` """


class Presence(pydantic.BaseModel):
    activities: List[Activity]
    """ List of activities for presence """
    status: Optional[StatusType] = StatusType.online
    """ Status of client, default to :attr:`StatusType.online` """
    afk: Optional[bool] = False
    """ Whether the client is AFK """
    since: Optional[float]
    """ Optional timestamp pointing to when client went idle, defaults to current call """

    @pydantic.validator("since", pre=True)
    def _validate_since(cls, _, **kwargs):
        idle = kwargs["values"]["status"] == StatusType.idle

        if not idle:
            return None

        if _:
            return _
        return time.time() * 1000


def game(name: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(
        activities=[
            Activity(
                name=name,
                type=ActivityType.GAME,
            )
        ],
        status=status,
    )


def listening(name: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(
        activities=[
            Activity(
                name=name,
                type=ActivityType.LISTENING,
            )
        ],
        status=status,
    )


def watching(name: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(
        activities=[
            Activity(
                name=name,
                type=ActivityType.WATCHING,
            )
        ],
        status=status,
    )


def competing(name: str, *, status: StatusType = StatusType.online) -> Presence:
    return Presence(
        activities=[
            Activity(
                name=name,
                type=ActivityType.COMPETING,
            )
        ],
        status=status,
    )


def streaming(
    name: str, url: str, *, status: StatusType = StatusType.online
) -> Presence:
    return Presence(
        activities=[
            Activity(
                name=name, 
                type=ActivityType.STREAMING, 
                url=url
            )
        ],
        status=status,
    )
