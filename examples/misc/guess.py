from acord import Client, Message, Intents
import random


class MClient(Client):
    async def on_ready(self):
        print(f"{self.user} is now online!")

    async def on_message_create(self, message: Message) -> None:
        if message.content.startswith(".guess"):
            number = random.randint(0, 20)
            _, *args = message.content.split(" ")
            if int(args[0]) == number:
                return await message.channel.send(content="Correct Guess")
            else:
                return await message.channel.send(
                    content=f"Wrong Guess. The number was {number}!"
                )


if __name__ == "__main__":
    client = MClient(intents=Intents.ALL)
    client.run("BOT TOKEN")
