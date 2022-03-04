.. meta::
   :title: Documentation - Acord [Guides]
   :type: website
   :url: https://acord.readthedocs.io/guides/application_commands.html
   :description: Guide on how to use application commands
   :theme-color: #f54646

.. currentmodule:: acord

********************
Application Commands
********************
Application commands are a new way of interacting with the discord API,
in acord they have never been easier to implement!

Classes
-------
* :class:`SlashBase`
* :class:`GenericModelCommand`
    * :class:`UserCommand`
    * :class:`MessageCommand`

Overview
--------
Application commands defined by the user must inherit the :class:`UDAppCommand`,
which stands for "User Defined Application Command".

In simple terms this is an unofficial object used to construct a payload to create an actual command.
It inherits :class:`~pydantic.BaseModel` and all attrs may be set through class vars.

Generating command using custom args
====================================
If your class requires another var,
you can simply extend the class vars and set a ``__ignore__`` var.

Example
^^^^^^^

.. code-block:: py

    from acord import UserCommand
    from typing import Any
    from xyz import Database

    db = Database()

    class FetchUserData(UserCommand, overwritable=False):
        client: Any
        name: str = "Fetch Data"

        __ignore__ = ("client",)

        async def callback(self, interaction, user) -> Any:
            # self.client is now accessible!
            ...

Now we have our class,
when intialising it we can simply pass the client kwarg through!

.. code-block:: py

    Client.register_application_command(FetchUserData(client=Client))

.. warning::
    Not setting the ``__ignore__`` var can lead to unexpected errors when converting command to json

Generic Commands
----------------
Generic models are used for commands which take no args from the user,
they are usually called via another component such as a message or user.

:class:`UserCommand` and :class:`MessageCommand` are both generic commands,
except they simply hardcode the type of the command.

Constructing A Generic Command
==============================

.. code-block:: py

    from acord import GenericModelCommand

    class MyCommand(GenericModelCommand):
        async def callback(self, interaction, *args):
            # Args are additional parameters that are sent with the callback
            # E.g with user commands a user object is sent
            return await interaction.respond(content="Look my response!")

.. warning::
    Generic commands have no type set,
    it is your job to set them!

Examples
--------
Examples of application commands can be found `here`_

.. _here: https://github.com/Mecha-Karen/acord/tree/main/examples/application_commands
