.. meta::
   :title: Documentation - Acord [API Reference]
   :type: website
   :url: https://acord.readthedocs.io/api/index.html
   :description: API Reference for working with the ACord lib
   :theme-color: #f54646

*************
API Reference
*************

Subclassing
~~~~~~~~~~~

Acord utilises the Pydantic library to speedup releases and also to keep the codebase clean.
However, 
this allows you to customise the bases however you wish, 
an example of this is with components.

.. code-block:: py

    from acord import Button, ButtonStyles

    class MyButton(Button):
        style: ButtonStyles = ButtonStyles.LINK
        label: str = "ACord"
        url: str = "https://acord.rtfd.io"

    # MyButton() now has all your vars filled out

Contents
~~~~~~~~

.. toctree::
    :titlesonly:

    bases
    client
    models
    voice
    webhooks
    ext/application_commands
