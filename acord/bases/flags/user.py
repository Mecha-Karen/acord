from enum import Flag


class UserFlags(Flag):
    """
    TODO: do the docstring
    """

    NONE = 0
    STAFF = 1 << 0
    PARTNER = 1 << 1

    HYPESQUAD = 1 << 2
    HYPESQUAD_BRAVERY = 1 << 6
    HYPESQUAD_BRILLIANCE = 1 << 7
    HYPESQUAD_BALANCE = 1 << 8

    BUG_HUNTER_LEVEL_1 = 1 << 3
    BUG_HUNTER_LEVEL_2 = 1 << 14

    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSEUDO_USER = 1 << 10

    VERIFIED_BOT = 1 << 15
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
