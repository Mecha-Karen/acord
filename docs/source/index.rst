.. meta::
   :title: Documentation - Acord
   :type: website
   :url: https://acord.readthedocs.io
   :description: Welcome to ACords's Documentation
   :theme-color: #f54646

*********************************
Welcome to Acords's Documentation
*********************************

.. raw:: html

    <div align="center">
        <img alt="PyPi - Version" src="https://img.shields.io/pypi/v/acord?logo=pypi&style=plastic">
        <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/acord">
        <img alt="PyPi - Python Versions" src="https://img.shields.io/pypi/pyversions/acord.svg">
        <img alt="PyPi - Status" src="https://img.shields.io/pypi/status/acord.svg">
        <a href='https://acord.readthedocs.io/en/latest/?badge=latest'>
            <img src='https://readthedocs.org/projects/acord/badge/?version=latest' alt='Documentation Status' />
        </a>    
    </div>

Welcome to Acords's Documentation, the place to find all the information about the Acord module. 
Acord is an efficient and reliable wrapper for the Discord API.

If you have any queries - `Click Here`_ to join our support server

.. _Click Here: https://discord.gg/Q5mFhUM

Alpha Notice
^^^^^^^^^^^^
ACord is currently a startup project is currently in its planning stage,
bugs may be expected in the library. 
Typos may exist in the docs.
But we rely on you to report this issues to help us make ACord better!

Features
========

* Modern pythonic API, ``async`` and ``await`` syntax
* Easy to use and modify
* Pydantic models and optional uv_loop installation
* Ratelimit handling
* Highly customisable
* Fast and efficient

Installation
============
Installing acord is as simple as ever!

**Stable**

.. code-block:: sh

    # windows
    pip install acord

    # linux
    pip3 install acord

**Development**

.. code-block:: sh

    git clone https://github.com/Mecha-Karen/acord
    cd acord

    # windows
    pip install .
    
    # linux
    pip3 install .


Basic Example
=============

.. code-block:: py

    from acord import Client, Message, Intents

    class MyClient(Client):
        async def on_message_create(self, message: Message) -> None:
            """ My message event handler! """

            if message.content.lower() == ".ping":
                return await message.channel.send(content="Pong!")

    if __name__ == "__main__":
        client = MyClient(intents=Intents.ALL)

        client.run("Bot Token")

Dependencies
============
Acord relies on ``Pydantic`` and ``aiohttp``, without them the module cannot function properly.
We also recommend installing the speedup package, which can be done using:

.. code-block:: sh

    # pip3 for Linux/MacOS
    pip install acord['speedup']

    # pip3 for Linux/MacOS
    pip install git+https://github.com/Mecha-Karen/ACord#egg=acord.speedup


Contents
========
.. toctree::
    :titlesonly:

    events.rst
    api/client.rst
    api/models.rst
    api/bases.rst
    guides/index.rst

* :ref:`genindex`
