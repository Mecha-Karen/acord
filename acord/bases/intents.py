from enum import Flag


class Intents(Flag):
    NONE                        = 0
    GUILDS                      = 1 << 0
    GUILD_MEMBERS               = 1 << 1
    GUILD_BANS                  = 1 << 2
    GUILD_EMOJIS_AND_STICKERS   = 1 << 3
    GUILD_INTEGRATIONS          = 1 << 4
    GUILD_WEBHOOKS              = 1 << 5
    GUILD_INVITES               = 1 << 6
    GUILD_VOICE_STATES          = 1 << 7
    GUILD_PRESENCES             = 1 << 8
    GUILD_MESSAGES              = 1 << 9
    GUILD_MESSAGE_REACTIONS     = 1 << 10
    GUILD_MESSAGE_TYPING        = 1 << 11
    DM_MESSAGES                 = 1 << 12
    DM_REACTIONS                = 1 << 13
    DM_TYPING                   = 1 << 14

    ALL = (
        GUILDS                      |
        GUILD_MEMBERS               |
        GUILD_BANS                  |
        GUILD_EMOJIS_AND_STICKERS   |
        GUILD_INTEGRATIONS          |
        GUILD_WEBHOOKS              |
        GUILD_INVITES               |
        GUILD_VOICE_STATES          |
        GUILD_PRESENCES             |
        GUILD_MESSAGES              |
        GUILD_MESSAGE_REACTIONS     |
        GUILD_MESSAGE_TYPING        |
        DM_MESSAGES                 |
        DM_REACTIONS                |
        DM_TYPING
    )
