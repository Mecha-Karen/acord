# Some helper objects used in the lib

from typing import Any
from copy import deepcopy
from acord.bases import ChannelTypes


GUILD_TEXT = [ChannelTypes.GUILD_TEXT, ChannelTypes.GUILD_NEWS]
DM_CHANNELS = [ChannelTypes.DM, ChannelTypes.GROUP_DM]


def _payload_dict_to_json(base, **keys) -> Any:
    # Converts kwargs to base excluding all keys
    base = base(**keys)
    to_exclude = list()
    
    for key, value in base.dict().items():
        if value is None and key not in keys:
            to_exclude.append(key)
    
    return base.json(exclude=set(to_exclude))


def _d_to_channel(DATA, conn):
    from acord.models import TextChannel, CategoryChannel, VoiceChannel, Stage

    if DATA['type'] in GUILD_TEXT:
        channel = TextChannel(conn=conn, **DATA), "text"
    elif DATA['type'] == ChannelTypes.GUILD_VOICE:
        print(DATA)
        channel = VoiceChannel(conn=conn, **DATA), "voice"
    elif DATA['type'] == ChannelTypes.GUILD_STAGE_VOICE:
        channel = Stage(conn=conn, **DATA)
    elif DATA['type'] == ChannelTypes.GUILD_CATEGORY:
        channel = CategoryChannel(conn=conn, **DATA), "category"
    elif DATA['type'] in DM_CHANNELS:
        # TODO: GROUP DM AND DM CHANNELS
        channel = DATA, "dm"
    else:
        raise ValueError('Unknown channel type encountered, %s, %s' % (
            DATA['type'], hasattr(ChannelTypes, DATA['type'])
        ))

    return channel


def copy(obj, **kwds) -> Any:
    return deepcopy(obj, **kwds)
