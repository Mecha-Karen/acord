from acord import ActionRow, Button, ButtonStyles, Client, Component, Interaction, InteractionType, Intents, Message
from typing import List, Any


class ConfirmRow(ActionRow):
    components: List[Component] = [
        Button(
            style=ButtonStyles.SUCCESS,
            label="Confirm",
            custom_id="confirm"
        ),
        Button(
            style=ButtonStyles.DANGER,
            label="Deny",
            custom_id="deny"
        )
    ]


class MyClient(Client):
    async def on_message_create(self, message: Message) -> Any:
        if message.content.lower() == ".confirm":
            return await message.reply(content="Confirm or deny example!", components=[ConfirmRow()])

    async def on_interaction_create(self, interaction: Interaction) -> Any:
        if interaction.type == InteractionType.MESSAGE_COMPONENT:
            c_id = interaction.data.custom_id

            if c_id == "confirm":
                return await interaction.respond(content="You have confirmed!")
            elif c_id == "deny":
                return await interaction.respond(content="You have denied!")

if __name__ == "__main__":
    client = MyClient(intents=Intents.ALL)
    client.run("TOKEN")
