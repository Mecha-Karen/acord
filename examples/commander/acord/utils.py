# Some helper objects used in the lib

from typing import Any
from copy import deepcopy

from acord.bases import ChannelTypes
from aiohttp import FormData


GUILD_TEXT = [ChannelTypes.GUILD_TEXT, ChannelTypes.GUILD_NEWS]
DM_CHANNELS = [ChannelTypes.DM, ChannelTypes.GROUP_DM]
VOICE_CHANNELS = [ChannelTypes.GUILD_VOICE, ChannelTypes.GUILD_STAGE_VOICE]
REQUIRED_KEYS = ["content", "files", "embeds", "sticker_ids"]


def _payload_dict_to_json(base, **keys) -> Any:
    # Converts kwargs to base excluding all keys
    base = base(**keys)
    to_exclude = list()

    for key, value in base.dict().items():
        if value is None and key not in keys:
            to_exclude.append(key)

    return base.json(exclude=set(to_exclude))


def _d_to_channel(DATA, conn):
    from acord.models import (
        TextChannel,
        CategoryChannel,
        VoiceChannel,
        DMChannel,
        GroupDMChannel,
    )

    if DATA["type"] in GUILD_TEXT:
        channel = TextChannel(conn=conn, **DATA), "text"
    elif DATA["type"] in VOICE_CHANNELS:
        channel = VoiceChannel(conn=conn, **DATA), "voice"
    elif DATA["type"] == ChannelTypes.GUILD_CATEGORY:
        channel = CategoryChannel(conn=conn, **DATA), "category"
    elif DATA["type"] == ChannelTypes.GROUP_DM:
        channel = GroupDMChannel(conn=conn, **DATA), "dm"
    elif DATA["type"] == ChannelTypes.DM:
        channel = DMChannel(conn=conn, **DATA), "dm"
    else:
        raise ValueError(
            "Unknown channel type encountered, %s, %s"
            % (DATA["type"], hasattr(ChannelTypes, DATA["type"]))
        )

    return channel


def message_multipart_helper(payload_class, exclude, inner_key=None, **kwds) -> FormData:
    """Helper for sending multipart form messages"""
    r_payload = payload_class(**kwds)
    payload = getattr(r_payload, inner_key) if inner_key else r_payload

    if not any(i for i in REQUIRED_KEYS if getattr(payload, i) is not None):
        raise ValueError("Message must contain one of: {}".format(
            ", ".join(REQUIRED_KEYS)
        ))

    if any(i for i in (payload.embeds or list()) if i.characters() > 6000):
        raise ValueError("Embeds cannot contain more then 6000 characters")

    form = FormData()

    if payload.files:
        for index, file in enumerate(payload.files):
            form.add_field(
                name=f"file{index}",
                value=file.fp,
                filename=file.filename,
                content_type="application/octet-stream",
            )

    if payload != r_payload:
        # Inner key was used for payload
        setattr(r_payload, inner_key, payload)

    form.add_field(
        name="payload_json",
        value=r_payload.json(exclude=exclude),
        content_type="application/json",
    )

    return form

def copy(obj, **kwds) -> Any:
    return deepcopy(obj, **kwds)
