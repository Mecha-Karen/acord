# Welcome to ACords getting started guide!
import acord


# Define your client!
class MyClient(acord.Client):
    # Add simple on_ready event
    async def on_ready(self):
        print(f'{self.user} is now online!')

    async def on_message(self, message: acord.Message):
        # Listen to all message, if content == ".ping"
        if message.content == ".ping":
            # Return "Pong!"
            return message.channel.send(content="Pong!")

if __name__ == "__main__":
    # Intialise client, using all intents
    client = MyClient(intents=acord.Intents.ALL)
    # Run your client!
    client.run(token=...)

    # TADA! your very own bot is now running.
