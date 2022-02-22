from typing import List
from acord import Client, Intents, Interaction, InteractionSlashOption
from acord.ext.application_commands import (
    AutoCompleteChoice, autocomplete,
    SlashBase, SlashOption, ApplicationCommandOptionType
)
import difflib


names = {
    "bob": 10, 
    "john": 20, 
    "bobby": 30, 
    "joe": 40,
    # Yes you would have alot more but im lazy
}


class AutoCompleteSlashExample(SlashBase, extendable=True, overwritable=False):
    options: List[SlashOption] = [
        SlashOption(
            type=ApplicationCommandOptionType.STRING,
            name="name",
            description="Name of person",
            required=True,
            autocomplete=True
        )
    ]
    name: str = "age-searcher"
    description: str = "Searches our db for the age of a person"

    async def callback(self, interaction: Interaction, name: InteractionSlashOption):
        age = names.get(name.value)

        if age is None:
            return await interaction.respond(content="Looks like this person does not exist")
        
        return await interaction.respond(content=f"{name.value.title()} is {age} years old.")

    @autocomplete("name")
    async def autoCompleteHandler(self, interaction: Interaction, option: InteractionSlashOption):
        val = option.value
        match = difflib.get_close_matches(val, names.keys())

        if not match:
            return

        return AutoCompleteChoice(name="name", value=match[0])

if __name__ == "__main__":
    client = Client(intents=Intents.ALL)
    client.register_application_command(AutoCompleteSlashExample())
