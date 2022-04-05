# File for holding smaller flags
from .base import BaseFlagMeta


class IMessageFlags(BaseFlagMeta):
    EPHEMERAL = 1 << 6
    """ only the user receiving the message can see it """
