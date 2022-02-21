from enum import Flag
from .base import BaseFlagMeta


class Intents(Flag, metaclass=BaseFlagMeta):
    """
    Intents are used for accessing certain content through the gateway,
    without them many of the events wouldn't work as expected

    .. rubric:: Usage

    All intents are assigned as a attribute,
    to combine intents, use the ``|`` operator, as shown below.

    .. code-block:: py

        from acord import Intents

        myIntents = (
            Intents.GUILDS
            | Intents.GUILD_MESSAGES
            | Intents.GUILD_PRESENCES
            ...
        )

    If bitwise operators are not to your taste,
    you can try using :meth:`BaseFlagMeta.__call__`.

    .. rubric:: Valid Attributes
    Listed below are the allowed intent attrs and what events they allow to be used

    * NONE
        - No intents
    * ALL
        - Every intent allowed through the gateway
    * GUILDS
        - GUILD_CREATE
        - GUILD_UPDATE
        - GUILD_DELETE
        - GUILD_ROLE_CREATE
        - GUILD_ROLE_UPDATE
        - GUILD_ROLE_DELETE
        - CHANNEL_CREATE
        - CHANNEL_UPDATE
        - CHANNEL_DELETE
        - CHANNEL_PINS_UPDATE
        - THREAD_CREATE
        - THREAD_UPDATE
        - THREAD_DELETE
        - THREAD_LIST_SYNC
        - THREAD_MEMBER_UPDATE
        - THREAD_MEMBERS_UPDATE
        - STAGE_INSTANCE_CREATE
        - STAGE_INSTANCE_UPDATE
        - STAGE_INSTANCE_DELETE
    * GUILD_MEMBERS
        - GUILD_MEMBER_ADD
        - GUILD_MEMBER_UPDATE
        - GUILD_MEMBER_REMOVE
        - THREAD_MEMBERS_UPDATE
    * GUILD_BANS
        - GUILD_BAN_ADD
        - GUILD_BAN_REMOVE
    * GUILD_EMOJIS_AND_STICKERS
        - GUILD_EMOJIS_UPDATE
        - GUILD_STICKERS_UPDATE
    * GUILD_INTEGRATIONS
        - GUILD_INTEGRATIONS_UPDATE
        - INTEGRATION_CREATE
        - INTEGRATION_UPDATE
        - INTEGRATION_DELETE
    * GUILD_WEBHOOKS
        - WEBHOOKS_UPDATE
    * GUILD_INVITES
        - INVITE_CREATE
        - INVITE_DELETE
    * GUILD_VOICE_STATES
        - VOICE_STATE_UPDATE
    * GUILD_PRESENCES
        - PRESENCE_UPDATE
    * GUILD_MESSAGES
        - MESSAGE_CREATE
        - MESSAGE_UPDATE
        - MESSAGE_DELETE
        - MESSAGE_DELETE_BULK
    * GUILD_MESSAGE_REACTIONS
        - MESSAGE_REACTION_ADD
        - MESSAGE_REACTION_REMOVE
        - MESSAGE_REACTION_REMOVE_ALL
        - MESSAGE_REACTION_REMOVE_EMOJI
    * GUILD_MESSAGE_TYPING
        - TYPING_START
    * DIRECT_MESSAGES
        - MESSAGE_CREATE
        - MESSAGE_UPDATE
        - MESSAGE_DELETE
        - CHANNEL_PINS_UPDATE
    * DIRECT_MESSAGE_REACTIONS
        - MESSAGE_REACTION_ADD
        - MESSAGE_REACTION_REMOVE
        - MESSAGE_REACTION_REMOVE_ALL
        - MESSAGE_REACTION_REMOVE_EMOJI
    * DIRECT_MESSAGE_TYPING
        - TYPING_START
    """

    NONE = 0
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_BANS = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16

    ALL = (
        GUILDS
        | GUILD_MEMBERS
        | GUILD_BANS
        | GUILD_EMOJIS_AND_STICKERS
        | GUILD_INTEGRATIONS
        | GUILD_WEBHOOKS
        | GUILD_INVITES
        | GUILD_VOICE_STATES
        | GUILD_PRESENCES
        | GUILD_MESSAGES
        | GUILD_MESSAGE_REACTIONS
        | GUILD_MESSAGE_TYPING
        | DIRECT_MESSAGES
        | DIRECT_MESSAGE_REACTIONS
        | DIRECT_MESSAGE_TYPING
        | MESSAGE_CONTENT
        | GUILD_SCHEDULED_EVENTS
    )
