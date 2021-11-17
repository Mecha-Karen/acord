<div align="center"><img src="./docs/_static/logo.png" height="100" width="100"></div>
<h1 align="center">ACord</h1>
<div align="center">
    <a href='https://acord.readthedocs.io/en/latest/'>
        <img src='https://readthedocs.org/projects/acord/badge/?version=latest' alt='Documentation Status' />
    </a>
</div>
<h4 align="center">A simple API wrapper for the discord API</h4>

## Features
* Uses modern pythonic, ``await`` and ``async`` syntax
* Flexible and customisable
* Rate limit handling
* Simple to modify, learn and contribute towards
* Optimised in speed and memory

## Installation
**Python >=3.8 is required**

### Stable
```sh
# Linux/Mac OS
pip3 install -U acord

# Windows
pip install -U acord
```
### Development
```sh
# Install directly from github

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
from acord import Client, Context, Message

class MyClient(Client):
    commands = [ping]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self) -> None:
        # WARNING: may be triggered more then once!
        # For a more controlled event use `on_connect`
        print(f'{self.user} is now ready!')

    async def ping(self, event: Context) -> Message:
        return event.respond(f"Ping: {self.latency()}")
```

## Links
* [Documentation](https://acord.readthedocs.io)
* [Support Server](https://discord.gg/JBjMAMag7a)
* [Discord API](https://discord.com/developers/docs/)
