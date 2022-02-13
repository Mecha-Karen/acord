from acord import ActionRow, Button, Client, Interaction, Intents, TextInput, Message, Modal
from typing import List


class MyModal(Modal):
    title: str = "Application 101"
    custom_id: str = "modal:submit_101"
    components: List[ActionRow] = [
        ActionRow(
            TextInput(
                custom_id="name",
                label="Name",
                style=1,
                placeholder="e.g John, Bob"
            )
        )
    ]


class MyClient(Client):
    async def on_message_create(self, message: Message):
        if message.content.lower() == ".application":
            return await message.reply(
                content="Form attached below",
                components=[
                    ActionRow(components=[Button(style=1, custom_id="open_modal:101", label="Form")])
                ]
            )
        
    async def on_interaction_create(self, interaction: Interaction):
        if interaction.data.custom_id == "open_modal:101":
            return await interaction.respond_with_modal(MyModal())
        if interaction.data.custom_id == "modal:submit_101":
            comp = interaction.data.components
            name = comp[0]["components"][0]["value"]
            # first index to get action row
            # second index to get our value from our form

            return await interaction.respond(content=f"Hello, {name}. I am {self.user.username}, nice to meet you!")


if __name__ == "__main__":
    client = MyClient(intents=Intents.ALL)
    client.run("TOKEN")
        
