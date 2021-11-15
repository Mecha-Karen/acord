""" Simple wrapper for handler intents """
DEFAULT_INTENT_VALUES = {
    "guilds": 1 << 0,
    "members": 1 << 1,
    "bans": 1 << 2,
    "emojis": 1 << 3,
    "integrations": 1 << 4,
    "webhooks": 1 << 5,
    "invites": 1 << 6,
    "voice": 1 << 7,
    "presence": 1 << 8,
    "messages": 1 << 9,
    "reactions": 1 << 10,
    "typing": 1 << 11,
    "dm_messages": 1 << 12,
    "dm_reactions": 1 << 13,
    "dm_typing": 1 << 14
}


class Intents(object):
    def __init__(self, **intents) -> None:
        values = [DEFAULT_INTENT_VALUES[k] for k, v in intents.items() if (v == True and v in DEFAULT_INTENT_VALUES)]
        print(values)
