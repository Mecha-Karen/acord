from __future__ import annotations
from enum import IntEnum


class StagePrivacyLevel(IntEnum):
    PUBLIC = 1
    """ The Stage instance is visible publicly,
    such as on Stage Discovery. """
    GUILD_ONLY = 2
    """ The Stage instance is visible to only guild members. """
