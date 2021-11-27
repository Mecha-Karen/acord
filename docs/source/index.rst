.. meta::
   :title: Documentation - Acord
   :type: website
   :url: https://acord.readthedocs.io
   :description: Welcome to ACords's Documentation
   :theme-color: #f54646

*********************************
Welcome to ACords's Documentation
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

Welcome to ACords's Documentation, the place to find all the information about the acord module. 
An API wrapper for the discord API.

If you have any queries - `Click Here`_ to join our support server

.. _Click Here: https://discord.gg/Q5mFhUM

Dependencies
============
Acord relies on ``Pydantic`` and ``aiohttp``, without them the functionality of the module is non-existant.
It is also recomended to install ``uvloop`` as it can speed up the program by a large margin.

Basic Example
-------------

.. code-block:: py

    from acord import Client, Message
    
    class MyClient(Client):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
        
        async def on_message(self, message: Message) -> None:
            """ My on_message event handler! """

            if message.content == "Hello":
                return await message.channel.send(f"Hello {message.author}, I am {self.user}!")


Contents
========

.. toctree::

    api/models.rst
