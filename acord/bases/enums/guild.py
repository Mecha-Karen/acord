from enum import IntEnum

class GuildMessageNotification(IntEnum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1

class ExplicitContentFilterLevel(IntEnum):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2

class MFALevel(IntEnum):
    NONE = 0
    ELEVATED = 1

class NSFWLevel(IntEnum):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3

class PremiumTierLevel(IntEnum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3

class VerificationLevel(IntEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4