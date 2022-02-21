from acord import ActionRow, SelectMenu, SelectOption, Client, Component, Interaction, Intents, Message
from typing import List, Any


class DropdownMenu(SelectMenu):
    options: List[SelectOption] = [
        SelectOption(label="1", description="Number 1", value=1),
        SelectOption(label="2", description="Number 2", value=2),
        SelectOption(label="3", description="Number 3", value=3)
    ]
    placeholder: str = "Pick a number"
    max_values: int = 1
    custom_id: str = "dropdown:number"


class DropdownRow(ActionRow):
    components: List[Component] = [DropdownMenu()]


class MyClient(Client):
    async def on_message_create(self, message: Message) -> Any:
        if message.content.lower() == ".dropdown":
            return await message.reply(content="Heres your dropdown", components=[DropdownRow()])

    async def on_interaction_create(self, interaction: Interaction):
        if interaction.data.custom_id == "dropdown:number":
            value = interaction.data.values[0]

            return await interaction.respond(content=f"You picked number {value}")

if __name__ == "__main__":
    client = MyClient(intents=Intents.All)
    client.run("TOKEN")
