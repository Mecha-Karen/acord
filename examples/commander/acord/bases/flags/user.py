from __future__ import annotations
from enum import Flag
from .base import BaseFlagMeta


class UserFlags(Flag, metaclass=BaseFlagMeta):
    """
    User flags allow you to identify users based on there badges given by discord

    .. rubric:: Usage

    Checking for single flags

    .. code-block:: py

        from acord import UserFlags

        isStaff = User.flags & UserFlags.STAFF == UserFlags.STAFF

    However, when checking for multiple flags, you need to use the ``|`` for all flags you want

    .. code-block:: py

        from acord import UserFlags
        flags = (
            UserFlags.STAFF
            | UserFlags.PARTNER
        )

        hasFlags = User.flags & flags == flags

    If bitwise operators are not to your taste,
    you can try using :meth:`BaseFlagMeta.__call__`.

    Attributes
    ----------
    NONE
        Value of 0, or **NO** flags
    STAFF
        discord staff flag
    PARTNER
        discord partner flag
    HYPESQUAD
        hypesquad events coordinator flag
    HYPESQUAD_BRAVERY
        hypesquad house bravery flag
    HYPESQUAD_BRILLIANCE
        hypesquad house brilliance flag
    HYPESQUAD_BALANCE
        hypesquad house bravery flag
    BUG_HUNTER_LEVEL_1
        bug hunter level 1 flag
    BUG_HINTER_LEVEL_2
        bug hunter level 2 flag
    PREMIUM_EARLY_SUPPORTER
        early Nitro Supporter
    TEAM_PSEUDO_USER
        user is a :class:`Team`
    VERIFIED_BOT
        verified bot flag
    VERIFIED_DEVELOPER
        early verified bot developer flag
    CERTIFIED_MODERATOR
        discord certified moderator flag
    """

    NONE = 0
    BOT_HTTP_INTERACTIONS = 1 << 19

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

    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18


class ApplicationFlags(Flag, metaclass=BaseFlagMeta):
    GATEWAY_PRESENCE = 1 << 12
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    GATEWAY_GUILD_MEMBERS = 1 << 14
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    EMBEDDED = 1 << 17
    GATEWAY_MESSAGE_CONTENT = 1 << 18
    GATEWAY_MESSAGE_CONTENT_LIMITED = 1 << 19
