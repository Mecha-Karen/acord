""" Simple echo slash command """
from traceback import print_exception
from typing import Any, Dict, List
from acord import (
    Client,
    SlashBase,
    SlashOption,
    Intents,
    Interaction,
    Snowflake,
    ApplicationCommandOptionType,
    AllowedMentions,
    InteractionSlashOption,
)

TESTING_GUILD_ID = ...  # Put your actual ID here


class Echo(SlashBase, extendable=True, overwritable=False):
    options: List[SlashOption] = [
        SlashOption(
            type=ApplicationCommandOptionType.STRING,
            name="string",
            description="String to echo",
            required=True,
        ),
    ]

    guild_ids: List[Snowflake] = [TESTING_GUILD_ID]

    name: str = "echo"
    description: str = "Echoes your message!"
    default_permission: bool = True

    async def callback(
        self, interaction: Interaction, **options: Dict[str, InteractionSlashOption]
    ) -> Any:
        return await interaction.respond(
            content=options["string"].value,
            allowed_mentions=AllowedMentions(deny_all=True),
        )

    async def on_error(self, interaction: Interaction, exc_info: tuple) -> Any:
        print_exception(*exc_info)
        return await interaction.respond(content="Oh no, An Error occurred!")


client = Client(intents=Intents.ALL)
client.register_application_command(Echo(client=client))

if __name__ == "__main__":
    client.run("TOKEN")
