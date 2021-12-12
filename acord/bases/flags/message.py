from .base import BaseFlagMeta
from enum import Flag


class MessageFlags(Flag, metaclass=BaseFlagMeta):
    """
    Message flags are used by discord to parse your message in a specified way.

    .. rubric:: Example
    
    For example, 
    :attr:`MessageFlags.SUPPRESS_EMBEDS` tells discord to not allow embeds

    All message flags are assigned as a attribute, 
    to combine flags, use the ``|`` operator, as shown below.

    .. code-block:: py

        from acord import MessageFlags

        myFlags = (
            MessageFlags.CROSSPOSTED
            | MessageFlags.IS_CROSSPOSTED
            ...
        )

    If bitwise operators are not to your taste, 
    you can try using :meth:`BaseFlagMeta.__call__`.
    """

    CROSSPOSTED = 1 << 0
    """this message has been published to subscribed channels"""

    IS_CROSSPOST = 1 << 1
    """this message originated from a message in another channel"""

    SUPPRESS_EMBEDS = 1 << 2
    """do not include any embeds when serializing this message"""

    SOURCE_MESSAGE_DELETED = 1 << 3
    """the source message for this crosspost has been deleted"""

    URGENT = 1 << 4
    """this message came from the urgent message system"""

    HAS_THREAD = 1 << 5
    """this message has an associated thread, with the same id as the message"""

    EPHERMERAL = 1 << 6
    """this message is only visible to the user who invoked the Interaction"""

    LOADING = 1 << 7
    """this message is an Interaction Response and the bot is \"thinking\""""
