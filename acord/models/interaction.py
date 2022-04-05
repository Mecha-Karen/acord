from __future__ import annotations
from typing import Any, List, Optional
import pydantic

from acord.models import Snowflake, Member, Message, User
from acord.bases import (
    Hashable,
    InteractionType,
    ComponentTypes,
    Modal,
)
from acord.core.abc import Route
from acord.ext.application_commands import (
    ApplicationCommandType,
    ApplicationCommandOptionType,
    AutoCompleteChoice,
)
import acord


class InteractionSlashOption(pydantic.BaseModel):
    name: str
    type: ApplicationCommandOptionType
    value: Any
    options: List[InteractionSlashOption] = []
    focused: bool = False


class InteractionData(pydantic.BaseModel):
    # All fields optional because they may not be provided with
    # all types of interactions
    id: Optional[Snowflake]
    name: Optional[str]
    type: Optional[ApplicationCommandType]
    resolved: Optional[Any]
    options: Optional[List[InteractionSlashOption]] = []
    custom_id: Optional[str]
    component_type: Optional[ComponentTypes]
    values: Optional[List[str]]
    target_id: Optional[Snowflake]
    components: Any


class Interaction(pydantic.BaseModel, Hashable):
    conn: Any
    hook: Any

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

    def __init__(self, **kwds) -> None:
        super().__init__(**kwds)

        self.hook = acord.Webhook(
            conn=self.conn,
            id=self.id,
            type=1,
            guild_id=self.guild_id,
            channel_id=self.channel_id,
            user=self.user or getattr(self.member, "user"),
            token=self.token,
            application_id=self.conn.client.user.id,
        )

    @pydantic.validator("user", "member", "message")
    def _validate_conns(cls, v, **kwargs):
        conn = kwargs["values"]["conn"]
        v.conn = conn
        return v

    @pydantic.validator("member", pre=True)
    def _validate_member(cls, member, **kwargs) -> Optional[Member]:
        if not member:
            return None

        guild_id = kwargs["values"]["guild_id"]
        conn = kwargs["values"]["conn"]
        return Member(conn=conn, guild_id=guild_id, **member)

    async def fetch_original_response(self) -> Any:
        """|coro|

        Fetches original message that was created when
        interaction responded.
        """
        return await self.hook.fetch_message("@original", use_application_id=True)

    async def delete_original_response(self) -> None:
        """|coro|

        Deletes original message that was created when
        interaction responded
        """
        return await self.hook.delete_message("@original", use_application_id=True)

    async def delete_response(self, message_id: Snowflake) -> None:
        """|coro|

        Deletes message that was created by this interaction

        Parameters
        ----------
        message_id: :class:`Snowflake`
            ID of message to delete
        """
        return await self.hook.delete_message(message_id, use_application_id=True)

    async def fetch_message(self, message_id: Snowflake):
        """|coro|

        Fetches a followup message created by interaction

        Parameters
        ----------
        message_id: :class:`Snowflake`
            ID of message to fetch
        """
        return await self.hook.fetch_message(message_id, use_application_id=True)

    async def respond_with_modal(self, modal: Modal) -> None:
        """|coro|

        Responds to an interaction using a modal.

        Parameters
        ----------
        modal: :class:`Modal`
            Modal to respond with
        """
        return await self.hook.respond_with_modal(modal)

    async def respond_to_autocomplete(self, choices: List[AutoCompleteChoice]) -> None:
        """|coro|

        Responds to an interaction with a list of choices

        Parameters
        ----------
        choices: List[:class:`AutoCompleteChoice`]
            List of choices to return the user,
            can be a list of dicts with the mapping name: value
        """
        return await self.hook.respond_to_autocomplete(choices)

    async def respond(self, **kwds) -> None:
        """|coro|

        Responds to an interaction.

        .. note::
            Refer to :meth:`Webhook.respond_with_message` for further guidance.
        """
        return await self.hook.respond_with_message(**kwds)

    async def send_followup(self, **kwds):
        """|coro|

        Sends a follow up message an interaction

        .. note::
            Refer to :meth:`Webhook.send_followup_message` for further guidance.
        """
        return await self.hook.send_followp(**kwds)

    async def edit_original_response(self, **kwds) -> None:
        """|coro|

        Edits original message created by interaction

        .. note::
            Refer to :meth:`Webhook.edit_message` for further guidance
        """
        return await self.edit_response("@original", **kwds)

    async def edit_message(self, message_id: Snowflake, **kwds) -> None:
        """|coro|

        Edits a follow up message sent by interaction

        .. note::
            Refer to :meth:`Webhook.edit_message` for further guidance
        """
        return await self.hook.edit_message(message_id, use_application_id=True, **kwds)
