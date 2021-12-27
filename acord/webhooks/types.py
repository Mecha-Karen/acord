from enum import IntEnum


class WebhookType(IntEnum):
    INCOMING = 1
    CHANNEL_FOLLOWER = 2
    APPLICATION = 3
