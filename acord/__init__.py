"""
ACord - An API wrapper for the discord API.

Created by Mecha Karen, and is licensed under the GNU GENERAL PUBLIC LICENSE.
"""
from typing import NamedTuple, Literal
import logging

from .bases import *
from .models import *

from .client import Client


logger = logging.getLogger("ACord")
__file__ = __import__("os").path.abspath(__file__)
__doc__ = "An API wrapper for the discord API"
__version__ = "0.0.1a"
__author__ = "Mecha Karen"


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    level: Literal["Pre-Alpha", "Alpha", "Beta", "Stable", "Final"]


version_info: VersionInfo = VersionInfo(major=0, minor=0, micro=1, level="Pre-Alpha")
