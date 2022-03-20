from acord.rest import InteractionServer, RestApi
from acord import SlashBase, Snowflake
from typing import List

TOKEN = "APPLICATION-TOKEN"
PUBLIC_KEY = "APPLICATION-PUBLIC-KEY"
TESTING_GUILD_ID = ...  # Actual guild id here

server = InteractionServer(host="0.0.0.0", port=8000)
rest = RestApi(TOKEN, server=server)

loop = rest.loop
loop.set_debug(True)


class Ping(SlashBase, extendable=True, overwritable=False):
    name: str = "ping"
    description: str = "Pong!"
    guild_ids: List[Snowflake] = [TESTING_GUILD_ID]

    async def callback(self, interaction) -> None:
        await interaction.respond(content="Pong!")


async def setup():
    rest.register_application_command(Ping())
    
    await server.setup(rest, PUBLIC_KEY)
    await rest.setup()


loop.run_until_complete(loop.create_task(setup()))
server.run_server()