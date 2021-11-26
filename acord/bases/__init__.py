from .flags.intents import Intents
from .flags.user import UserFlags
from .flags.channels import ChannelTypes, VoiceQuality

from .file import File
from .mixins import Hashable, _C, T, H


class MISSING(object):
    """ Identifer class, used to represent a value which doesn't exist, or should be set to 0 """