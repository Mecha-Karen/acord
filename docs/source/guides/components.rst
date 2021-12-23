.. meta::
   :title: Documentation - Acord [Guides]
   :type: website
   :url: https://acord.readthedocs.io/guides/components.html
   :description: Guides on how to use message components
   :theme-color: #f54646

.. currentmodule:: acord

.. _ComponentsGuide:

****************
Components Guide
****************
Components are a simple yet elegant feature in discord,
here is how you can use them in acord!

Classes
-------
* :class:`Button`
* :class:`SelectMenu`
    - :class:`SelectOption`
* :class:`ActionRow`

Action Rows
-----------
Action rows are what will hold all your components like buttons.
Action rows may not contain buttons and action rows.

You can define them by doing the following:

.. code-block:: py

    from acord import ActionRow

    row = ActionRow(components=[...])
    row = ActionRow(..., )
    
    row = ActionRow()

    for component in ...:
        row.add_component(component)

Buttons
-------
Buttons are something you can click,
you can set the style of your button using :class:`ButtonStyle`.

You can define them by doing the following:

.. code-block:: py

    from acord import Button

    button = Button(..., )
    ActionRow.add_component(button)

Select Menus
------------
Select Menus are drop downs which allow users to select one or multiple objects.

You can define them by doing the following:

.. code-block:: py

    from acord import SelectMenu, SelectOption

    select = SelectMenu(
        options=[SelectOption, SelectOption]
    )

    select = SelectMenu()
    select.add_option(SelectOption)

Sending A Message
-----------------
Sending a message is simple!
All you need to do is provide a list of action rows,
as shown below.

.. code-block:: py

    from acord import ActionRow, Button

    message: Message = ...
    row = ActionRow(
        acord.Button(
            style=acord.ButtonStyles.LINK, 
            label="Documentation", 
            url="https://acord.rtfd.io"
        )
    )

    return message.channel.send(content="Some Components", components=[row])

Responding
----------
Lets say, somebody clicks that button of yours.
And you want to respond with a nice message,
well its never been more simpler!

So lets get started, first send your message.
In the demo below it will be defined as ``message``

.. code-block:: py

    message: Message = ...

    inter = await Client.wait_for("interaction", callback=None, timeout=None)

    await inter.respond(content="Look a response!")

The respond function can be found here, :meth:`Interaction.respond`.

But in a nutshell, its the same as sending any message!

*Psst*, you may wanna check out :meth:`Client.wait_for` for some examples.
