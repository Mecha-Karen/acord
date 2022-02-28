.. meta::
   :title: Documentation - Acord [Guides]
   :type: website
   :url: https://acord.readthedocs.io/guides/low_level_api.rst
   :description: Working with the lower level API with ACord
   :theme-color: #f54646


.. currentmodule:: acord


*************
Low Level API
*************
ACord exposes its lower level API,
just incase you need to use it.
We also allow you to customise the functionality of the library very easily,
so be awair of what your doing.
So lets start simple.

Core [HTTP Control]
~~~~~~~~~~~~~~~~~~~
So lets dive into customising the HTTP side of ACord.

Signals
=======
Signals are files which contain OPCodes and Status Codes.
They are used by ACord to monitor and identify changes or issues raised by discord.

For example ``acord.core.signals.gateway``, 
contains all the stuff ACord may use for tracking states and commands sent by discord.
If we receive, OPCode 0, we know is a DISPATCH event.
So we will also dispatch the event through to the higher level API.

Now with errors, it works exactly the same way.
If the WebSocket closes with ``4004``,
we know that ``AUTH_FAILED``.
So we will raise it so the user can correct their mistake.

ABC
===
The ABC file contains all the bits of information ACord uses to interact with the REST API.
You can change the API Version, API Url and so on.

.. code-block:: py
    
    import acord.core.abc as core_abc

    core_abc.API_VERSION = 9

    # Continue with your code as usualy

This file also contains the ``Route`` object and ``buildURL`` function.
They can be used to make routes and URLs for the REST API.
Which can then be used by ACord to make requests to that route with the desired method.

Decoders
========
Nothing special goes on in here,
just some helper functions to process gateway messages and HTTP responses.

The ``decompressResponse`` helps in decompressing the zlib-compressed message.
And, ``decodeResponse`` is a higher level function which can decode both string and bytes.

``ETF`` is currently not supported,
but will be in future versions.

.. tip::
    You can change these functions by overwriting them like this:

    .. code-block:: py

        import acord.core.decoders as dec
        import json

        dec.JSON = json.loads

Heartbeats
==========
Heartbeats are used by ACord to keep WebSocket connections alive.
Now this is pretty much useless unless you wanna build your own heartbeater.

Heartbeat ABC Class
^^^^^^^^^^^^^^^^^^^

.. autoclass:: acord.core.heartbeat.KeepAlive
    :members:

Implementations
^^^^^^^^^^^^^^^

You will need to use the :class:`KeepAlive` ABC,
which has the following methods you need to provide:

* send_heartbeat(self) -> Sends heartbeat through the WebSocket
* get_payload(self) -> Returns a payload for the heartbeat
* ack(self) -> Called when the WebSocket ACKs our heartbeat

And the following attrs which is used by ``.run(self)`` func.
You wont need this if you overwrite this function.

* _ended: :class:`bool` : Whether the client has stopped heartbeating
* _interval: :class:`int` : Time in seconds to wait for till next heartbeat

.. hint::
    Take a peak at the default implementations of the heartbeat system,
    it may or may not help but will surely guide you along the way.

.. note::
    As of version 0.2.3a0,
    users will need to overwrite the imported class name,
    in the same way as decoders.

HTTPClient
==========
Now the fun class,
this class is responsible for making HTTP Request to the REST API.

.. hint::
    You can already access this through :attr:`Client.http`,
    or any model which has the conn attr.

HTTPClient Class
^^^^^^^^^^^^^^^^

.. autoclass:: acord.core.http.HTTPClient
    :members:

Making Requests
^^^^^^^^^^^^^^^
Once you have got your HTTP class,
you can do many things.
One of which is make requests.

In this example we will simply leave a guild.

.. note::
    We recomend to use :meth:`Guild.leave`.

.. code-block:: py

    from acord.core.abc import Route

    GUILD_ID = Snowflake(..., )  # Actual guild id here
    client = ...    # Your HTTPClient object

    async with client as conn:
        async with conn.request(
            Route("DELETE", path=f"/users/@me/guilds/{GUILD_ID}"),
        ) as request:
            if request.status == 204:
                print("Left the guild! :D")

This is an advantage to any user who like having this control,
it can also allow you to have access to API Routes before ACord has added them!

Ratelimiters
============
Ratelimiters will be covered later,
which will be available soon.
