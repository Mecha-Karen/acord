.. meta::
   :title: Documentation - Acord [Client]
   :type: website
   :url: https://acord.readthedocs.io/api/client.html
   :description: Base client for interacting with API
   :theme-color: #f54646

.. currentmodule:: acord

******
Client
******
ACord's built in client enables rapid development, but this doesn't mean you can't create your own!

Example
~~~~~~~

.. code-block:: py

    from acord import Client, Message, Intents
    from typing import Any

    class MyClient(Client):
        async def on_message_create(self, message: Message) -> Any:
            if message.content == ".ping":
                return message.reply(content="Pong!")
    
    if __name__ == "__main__":
        client = MyClient(token="My token", intents=Intents.ALL)
        client.run()

Client
~~~~~~

.. attributetable:: Client

.. autoclass:: Client
    :members:

Shard
~~~~~

.. attributetable:: Shard

.. autoclass:: Shard
    :members:
