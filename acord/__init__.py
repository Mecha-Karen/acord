"""
ACord - An API wrapper for the discord API.

Created by Mecha Karen, and is licensed under the GNU GENERAL PUBLIC LICENSE.
"""
from typing import NamedTuple, Literal, List, Optional
import logging

from .bases import *
from .models import *

from .client import Client


logger = logging.getLogger("ACord")
__file__ = __import__("os").path.abspath(__file__)
__doc__ = "An API wrapper for the discord API"
__version__ = "0.0.1a3"
__author__ = "Mecha Karen"

SelectOption.__annotations__['emoji'] = Optional[PartialEmoji]
Button.__annotations__['emoji'] = Optional[PartialEmoji]
TextChannel.fetch_invites.__annotations__["return"] = List[Invite]
TextChannel.create_invite.__annotations__["return"] = List[Invite]
Invite.__annotations__["guild"] = Optional[Guild]


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    level: Literal["Pre-Alpha", "Alpha", "Beta", "Stable", "Final"]


version_info: VersionInfo = VersionInfo(major=0, minor=0, micro=1, level="Pre-Alpha")
