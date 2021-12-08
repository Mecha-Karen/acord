.. meta::
   :title: Documentation - Acord [Events]
   :type: website
   :url: https://acord.readthedocs.io/events.html
   :description: Acord event reference
   :theme-color: #f54646

.. currentmodule:: acord

******
Events
******
Event reference, names and parameters passed when calling events

When registering events in the client class, 
they must be an async function and be called ``on_event-name``.

If using the :meth:`Client.on` decorater,
its preferred to not start the event with ``on_``.
However, it will still be accepted.

on_connect
~~~~~~~~~~
Called when the client first connects to the gateway

on_ready
~~~~~~~~
Called when gateway dispatched ``READY``.
Indicating that the client has successfully connected to the gateway.

on_heartbeat
~~~~~~~~~~~~
Called when the client has sent a heartbeat and has recieved a successful response.

on_message
~~~~~~~~~~
Called when gateway dispatches ``MESSAGE_CREATE``.
Indicating that a message has just been created.

Parameters
==========

message: :class:`Message`
    Message that was just created

on_guild_create
~~~~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_CREATE``.
Indicating the client has joined a new guild, 
this is different to ``on_guild_recv``.

Parameters
==========
guild: :class:`Guild`
    Guild client has just joined

on_guild_recv
~~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_CREATE``.
When the client recieves a guild clients joined in.

Parameters
==========
guild: :class:`Guild`
    Guild clients in

on_guild_delete
~~~~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_DELETE``.
Indicating that the client has just been removed from a server,
this is different to ``on_guild_outage``

Parameters
==========
guild: :class:`Guild`
    Guild client was removed from

on_guild_outage
~~~~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_DELETE``.
Indicating the client is in a guild that is unavailable due to an outage.

Parameters
==========
guild: :class:`Guild`
    Guild thats experiencing an outage, :attr:`Guild.unavailable` should be true.
