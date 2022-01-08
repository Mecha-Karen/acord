from enum import IntEnum


class ScheduledEventEntityType(IntEnum):
    STAGE_INSTANCE = 1
    VOICE = 2
    EXTERNAL = 3


class ScheduledEventPrivacyLevel(IntEnum):
    GUILD_ONLY = 2
    """ the scheduled event is only accessible to guild members """


class ScheduledEventStatus(IntEnum):
    SCHEDULED = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELED = 4
