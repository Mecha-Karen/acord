from acord import Client, Message, Intents
import random
class MClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    async def on_ready(self):
         print(f'------------\n{self.user.username}#{self.user.discriminator}\n------------\n{self.user.id}')
    async def on_message(self, message: Message) -> None:
        if message.content.startswith(".guess"):
            number = random.randint(0, 20)
            if int(message.content.split('.guess')[1]) == number:
                return await message.channel.send(content='Correct Guess')
            else:
                return await message.channel.send(content=f'Wrong Guess. The number was {number}!')
          
if __name__ == "__main__":
    client = MClient(intents=Intents.ALL)
    client.run("BOT TOKEN")