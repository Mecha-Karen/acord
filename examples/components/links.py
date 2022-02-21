from acord import ActionRow, Button, ButtonStyles, Client, Component, Intents, Message
from typing import Any, List


class LinksRow(ActionRow):
    components: List[Component] = [
        Button(
            style=ButtonStyles.LINK,
            label="Youtube",
            url="https://youtube.com/"
        ),
    ]


class MyClient(Client):
    async def on_message_create(self, message: Message) -> Any:
        if message.content.lower() == ".links":
            return await message.reply(content="Wow, a button with a link appeared", components=[LinksRow()])

if __name__ == "__main__":
    client = MyClient(intents=Intents.ALL)
    client.run("TOKEN")
