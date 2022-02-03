""" Simple bookmark message command """
from traceback import print_exception
from typing import Any, List, Union
from acord import (
    Client, MessageCommand, Intents,
    Interaction, Message, Snowflake
)

TESTING_GUILD_ID = 740523643980873789  # Put your actual ID here
bookmarks: dict = {}


class Bookmark(MessageCommand, extendable=True, overwritable=True):
    client: Any
    name: str = "Bookmark"
    guild_ids: List[Snowflake] = [TESTING_GUILD_ID]

    __ignore__ = ("client",)

    async def callback(self, interaction: Interaction, message: Union[Message, Snowflake]) -> Any:
        if isinstance(message, int):
            message = await self.client.fetch_message(interaction.channel_id, message)

        user_id = interaction.member.user.id

        if user_id not in bookmarks:
            bookmarks[user_id] = []

        # Do some stuff with the bookmarked channel and message ID.
        # Im just too lazy
        bookmarks[user_id].append((message.channel_id, message.id))

        return await interaction.respond(
            content=f"Bookmarked message from {message.author}"
        )

    async def on_error(self, interaction: Interaction, exc_info: tuple) -> Any:
        print_exception(*exc_info)
        return await interaction.respond(content="Oh no, an error occured!")


client = Client(intents=Intents.ALL)
client.register_application_command(Bookmark(client=client))

if __name__ == "__main__":
    client.run("NzQxNzE0NTcxNjYzNzY5NjUw.Xy7lhg.r-QKEtP6pA_JQ0xzhtTSk3006dU")
