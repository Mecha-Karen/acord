from __future__ import annotations
from typing import Any, List, Optional, Union
from aiohttp import FormData
import pydantic

from acord.models import Snowflake, Member, User, Message, message
from acord.bases import (
    Hashable, 
    InteractionType,
    InteractionCallback,
    ComponentTypes, 
    SelectOption,
)
from acord.payloads import MessageCreatePayload
from acord.core.abc import Route
from acord.bases.flags.base import BaseFlagMeta


class IMessageFlags(BaseFlagMeta):
    EPHEMERAL = 1 << 6
    """ only the user receiving the message can see it """


class IMessageCreatePayload(MessageCreatePayload):
    flags: Optional[int]


class InteractionData(pydantic.BaseModel, Hashable):
    id: Optional[Snowflake]
    name: Optional[str]
    type: Any
    resolved: Optional[Any]
    options: Optional[List[Any]]
    custom_id: Optional[str]
    component_type: Optional[ComponentTypes]
    values: Optional[List[SelectOption]]
    target_id: Optional[Snowflake]


class _FormPartHelper(pydantic.BaseModel):
    type: InteractionCallback
    data: IMessageCreatePayload


class Interaction(pydantic.BaseModel, Hashable):
    conn: Any

    id: Snowflake
    """ ID of interaction """
    application_id: Snowflake
    """ id of the application this interaction is for """
    type: InteractionType
    """ the type of interaction """ 
    token: str
    """ a continuation token for responding to the interaction """
    version: int
    """ read-only property, always ``1`` """
    data: Optional[InteractionData]
    """ the command data payload """
    guild_id: Optional[Snowflake]
    """ the guild it was sent from """
    channel_id: Optional[Snowflake]
    """ the channel it was sent from """
    member: Optional[Member]
    """ guild member data for the invoking user, including permissions """
    user: Optional[User]
    """ user payloadject for the invoking user, if invoked in a DM """
    message: Optional[Message]
    """ for components, the message they were attached to """

    @pydantic.validator("member", pre=True)
    def _validate_member(cls, member, **kwargs) -> Optional[Member]:
        if not member:
            return

        guild_id = kwargs["values"]["guild_id"]
        conn = kwargs["values"]["conn"]
        return Member(conn=conn, guild_id=guild_id, **member)

    async def fetch_original_response(self) -> Message:
        """|coro|

        Fetches original message that was created when
        interaction responded.
        """
        return await self.fetch_message("@original")

    async def delete_original_response(self) -> None:
        """|coro|

        Deletes original message that was created when
        interaction responded
        """
        return await self.delete_response("@original")

    async def delete_response(self, message_id: Snowflake) -> None:
        """|coro|

        Deletes message that was created by this interaction
        """
        await self.conn.request(
            Route("GET", path=f"/webhooks/{self.application_id}/{self.token}/messages/{message_id}")
        )

    async def fetch_message(self, message_id: Snowflake):
        """|coro|

        Fetches a followup message created by interaction
        """
        r = await self.conn.request(
            Route("GET", path=f"/webhooks/{self.application_id}/{self.token}/messages/{message_id}")
        )

        return Message(**(await r.json()))

    async def respond(self, *, ack: bool = False, followup: bool = False, **data) -> None:
        """|coro|

        Responds to an interaction.
        
        Parameters
        ----------
        flags: :class:`IMessageFlags`
            Additional flags for interaction followups.
        ack: :class:`bool`
            Whether to return a loading status,
            requires you to resend request using,
            :meth:`Interaction.edit`
        followup: :class:`bool`
            Whether the message is a followup and not a response.

        Rest of the parameters are the same as,
        :meth:`TextChannel.send`
        """
        if ack:
            rmsType = InteractionCallback.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
        else:
            rmsType = InteractionCallback.CHANNEL_MESSAGE_WITH_SOURCE

        payload = IMessageCreatePayload(**data)

        if not any(
            i for i in payload.dict() if i in ["content", "files", "embeds", "sticker_ids"]
        ):
            raise ValueError(
                "Must provide one of content, file, embeds, sticker_ids inorder to send a message"
            )

        if any(i for i in (payload.embeds or list()) if i.characters() > 6000):
            raise ValueError("Embeds cannot contain more then 6000 characters")

        form_data = FormData()

        if payload.files:
            for index, file in enumerate(payload.files):

                form_data.add_field(
                    name=f"file{index}",
                    value=file.fp,
                    filename=file.filename,
                    content_type="application/octet-stream",
                )

        if not followup:
            payload = _FormPartHelper(
                type=rmsType,
                data=payload
            )

        form_data.add_field(
            name="payload_json",
            value=payload.json(exclude={"files"}),
            content_type="application/json",
        )

        if not followup:
            ending = "/callback"
        else:
            ending = "/"

        await self.conn.request(
            Route("POST", path=f"/interactions/{self.id}/{self.token}{ending}"),
            data=form_data,
        )

    async def edit(self, *, ack: bool = False, **data) -> None:
        """|coro|

        Edits original message created by interaction

        Parameters
        ----------
        ack: :class:`bool`
            ACK an interaction and edit the original message later;
            the user does not see a loading state
        
        Rest of the parameters are the same as,
        :meth:`TextChannel.send`
        """
        return await self.edit_response("@original", ack=ack, **data)

    async def edit_response(self, message_id: Snowflake, *, ack: bool = False, **data) -> None:
        """|coro|

        Edits a follow up message sent by interaction

        Parameters
        ----------
        message_id: :class:`Snowflake`
            ID of message to edit
        ack: :class:`bool`
            ACK an interaction and edit the original message later;
            the user does not see a loading state

        Rest of the parameters are the same as,
        :meth:`TextChannel.send`
        """
        if ack:
            rmsType = InteractionCallback.DEFERRED_UPDATE_MESSAGE
        else:
            rmsType = InteractionCallback.UPDATE_MESSAGE

        payload = IMessageCreatePayload(**data)

        if not any(
            i for i in payload.dict() if i in ["content", "files", "embeds", "sticker_ids"]
        ):
            raise ValueError(
                "Must provide one of content, file, embeds, sticker_ids inorder to send a message"
            )

        if any(i for i in (payload.embeds or list()) if i.characters() > 6000):
            raise ValueError("Embeds cannot contain more then 6000 characters")

        form_data = FormData()

        if payload.files:
            for index, file in enumerate(payload.files):

                form_data.add_field(
                    name=f"file{index}",
                    value=file.fp,
                    filename=file.filename,
                    content_type="application/octet-stream",
                )

        form_data.add_field(
            name="payload_json",
            value=payload.json(exclude={"files"}),
            content_type="application/json",
        )

        await self.conn.request(
            Route("PATCH", path=f"/webhooks/{self.application_id}/{self.token}/messages/{message_id}"),
            data=form_data,
        )
