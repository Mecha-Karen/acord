""" Simple high five user command """
""" Simple bookmark message command """
from traceback import print_exception
from typing import Any, List, Union
from acord import Client, UserCommand, Intents, Interaction, User, Snowflake

TESTING_GUILD_ID = ...  # Put your actual ID here


class HighFive(UserCommand, extendable=True, overwritable=False):
    client: Any
    name = "High Five"
    guild_ids: List[Snowflake] = [TESTING_GUILD_ID]

    __ignore__ = ("client",)

    async def callback(self, interaction: Interaction, user: Union[User, Snowflake]):
        if isinstance(user, int):
            user = await self.client.fetch_user(user)

        return await interaction.respond(
            content=f"{user} got high fived from {interaction.member.user}",
        )

    async def on_error(self, interaction, exc_info):
        print_exception(*exc_info)
        return await interaction.respond(content="Oh no, An Error occurred!")


client = Client(intents=Intents.ALL)
client.register_application_command(HighFive(client=client))

if __name__ == "__main__":
    client.run("TOKEN")
