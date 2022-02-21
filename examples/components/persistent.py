# No, just use on_interaction_create and tada.
# You will find out that your button will work even after restarting.
# But just incase, here you go

from acord import ActionRow, Button, ButtonStyles, Client, Component, Interaction, InteractionType, Intents, Message
from typing import List, Any


class ButtonRow(ActionRow):
    components: List[Component] = [
        Button(
            style=ButtonStyles.SUCCESS,
            label="Click me",
            custom_id="persistant:1"
        )
    ]


class MyClient(Client):
    async def on_message_create(self, message: Message) -> Any:
        if message.content.lower() == ".spawn":
            return await message.channel.send(content="Click the button below", components=[ButtonRow()])

    async def on_interaction_create(self, interaction: Interaction) -> Any:
        if interaction.type == InteractionType.MESSAGE_COMPONENT:
            c_id = interaction.data.custom_id

            if c_id == "persistant:1":
                return await interaction.respond(content="Look, I can persistantly respond")

if __name__ == "__main__":
    client = MyClient(intents=Intents.ALL)
    client.run("TOKEN")
