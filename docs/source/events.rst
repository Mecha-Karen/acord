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

on_resume
~~~~~~~~~
Called when client connection resumed,
meaning that the connection was reset by peer and needed to be reconnected.

.. warning::
    You may notice changes in certain objects so track user made caches.

on_message
~~~~~~~~~~
Called when gateway dispatches ``MESSAGE_CREATE``.
Indicating that a message has just been created.

Parameters
==========

message: :class:`Message`
    Message that was just created

on_message_pin
~~~~~~~~~~~~~~
Called when gateway dispatches ``CHANNEL_PINS_UPDATE``.
Indicating a message has been pinned/unpinned.

.. note::
    This event is not called when pinned message is deleted

Parameters
==========

channel: :class:`Channel`
    Channel were message was pinned/unpinned in

timestamp: :py:`datetime.datetime`
    The timestamp of when message was pinned/unpinned

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

on_guild_update
~~~~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_UPDATE``.
Indicating that a guild has been modifed.

Parameters
==========
guild: :class:`Guild`
    Guild that has been updated

on_guild_ban
~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_BAN_ADD``.
Indicating a user has been banned

Parameters
==========
guild: :class:`Guild`
    Guild were user was banned from
user: :class:`User`
    User who was banned

on_guild_ban_remove
~~~~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_BAN_REMOVE``.
Indicating a user has been unbanned

Parameters
==========
guild: :class:`Guild`
    Guild were user was unbanned from
user: :class:`User`
    User who was unbanned

on_emoji_update
~~~~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_EMOJIS_UPDATE``.
Indicating an emoji has been updated.
This is different to ``on_emojis_update``,
as this is a singular emoji not all of them.

Parameters
==========
emoji: :class:`Emoji`
    Emoji just updated

on_emojis_update
~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``GUILD_EMOJIS_UPDATE``.
Indicating many emojis have been updated.
this is different to ``on_emoji_update``,
as this contains all updated emojis instead of 1.

Parameters
==========
emojis: List[:class:`Emoji`]
    List of updated emojis

on_channel_create
~~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``CHANNEL_CREATE``.
This is called when any channels are created.

Parameters
==========
channel: :class:`Channel`
    Channel just created

on_channel_update
~~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``CHANNEL_UPDATE``.
This is called when any channels are updated.

Parameters
==========
channel: :class:`Channel`
    Channel that was just updated

on_channel_delete
~~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``CHANNEL_DELETE``.
Indicating a channel has been deleted

Parameters
==========
channel: :class:`Channel`
    Channel that was just deleted

on_thread_create
~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``THREAD_CREATE``.
Indicating that a thread has been created.

Parameters
==========
thread: :class:`Thread`
    Thread thats just been created

on_thread_update
~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``THREAD_UPDATE``.
Indicating that a thread has been updated.

Parameters
==========
thread: :class:`Thread`
    Thread thats just been updated

on_thread_delete
~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``THREAD_DELETE``.
Indicating that a thread has been deleted.

Parameters
==========
thread: :class:`Thread`
    Thread thats just been deleted

on_thread_sync
~~~~~~~~~~~~~~
Called when the gateway dispatches ``THREAD_LIST_SYNC``.
Indicating that the client has gotten access to new threads.

Parameters
==========
threads: List[:class:`Thread`]
    A list of threads that the client has gained access to.

on_thread_member_update
~~~~~~~~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``THREAD_MEMBER_UPDATE``.

Parameters
==========
thread_member: :class:`ThreadMember`
    Member that has been updated

on_thread_members_update
~~~~~~~~~~~~~~~~~~~~~~~
Called when the gateway dispatches ``THREAD_MEMBERS_UPDATE``.

Parameters
==========
thread_member: :class:`Thread`
    Updated thread, were :attr:`Thread.members` is updated
