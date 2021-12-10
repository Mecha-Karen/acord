from .flags.base import BaseFlagMeta
from .flags.intents import Intents
from .flags.user import UserFlags
from .flags.channels import ChannelTypes, VoiceQuality
from .flags.permissions import Permissions

from .embeds import (
    EmbedFooter,
    EmbedAuthor,
    EmbedField,
    EmbedImage,
    EmbedThumbnail,
    EmbedVideo,
    EmbedProvidor,
    Embed
    )
from .file import File
from .mixins import Hashable, _C, T, H
from .mentions import AllowedMentions


class MISSING(object):
    """Identifer class, used to represent a value which doesn't exist, or should be set to 0"""
