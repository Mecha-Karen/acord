<div align="center"><img src="./docs/source/_static/logo.png" height="100" width="100"></div>
<h1 align="center">ACord</h1>
<div align="center">
    <a href='https://acord.readthedocs.io/en/latest/'>
        <img src='https://readthedocs.org/projects/acord/badge/?version=latest' alt='Documentation Status' />
    </a>
</div>
<h4 align="center">A simple API wrapper for the discord API</h4>

License: **GPL-3.0 License** (see the LICENSE file for details) covers all files in the **acord** repository unless stated otherwise.

> This library is in its planning stage, so bugs may be encountered and breaking changes will occur!

## Features
* Uses modern pythonic, ``await`` and ``async`` syntax
* Flexible and customisable
* Rate limit handling
* Simple to modify, learn and contribute towards
* Optimised in speed and memory

## Installation
**Python >=3.8 is required**

### Development
```sh
# Install directly from github, this is the best option as of now!

## Linux/Mac OS
pip3 install -U git+https://github.com/Mecha-Karen/acord

## Windows
pip install -U git+https://github.com/Mecha-Karen/acord

# From source
git clone https://github.com/Mecha-Karen/acord

## pip for windows
pip3 install .
```

## Example

### Client
```py
from acord import Client, Message, Intents

class MyClient(Client):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def on_message_create(self, message: Message) -> None:
        """ My message event handler! """

        if message.content.lower() == ".ping":
            return await message.channel.send(content="Pong!")

if __name__ == "__main__":
    client = MyClient(intents=Intents.ALL)

    client.run("Bot Token")
```

## Links
* [Documentation](https://acord.readthedocs.io)
* [Support Server](https://discord.gg/JBjMAMag7a)
* [Discord API](https://discord.com/developers/docs/)
