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

If using the :meth:`Client.on` decorator,
its preferred to not start the event with ``on_``.
However, it will still be accepted.

on_resume
~~~~~~~~~
Called when client session resumes

Parameters
^^^^^^^^^^
This event has no parameters

on_heartbeat
~~~~~~~~~~~~
Called when client responds to a heartbeat ack,
an acknowledged heartbeat from discord.

Parameters
^^^^^^^^^^
This event has no parameters

on_ready
~~~~~~~~
Called when discord dispatches its ready event,
noting the client has connected successfully and will begin receiving data such as joined guilds

Parameters
^^^^^^^^^^
This event has no parameters

on_interaction_create
~~~~~~~~~~~~~~~~~~~~~
Called when an interaction has been created via button clicks or application commands.

Parameters
^^^^^^^^^^
interaction: :class:`Interaction`
    Interaction created

on_interaction_update
~~~~~~~~~~~~~~~~~~~~~
Called when an interaction has been updated

Parameters
^^^^^^^^^^
interaction: :class:`Interaction`
    Interaction updated

on_interaction_delete
~~~~~~~~~~~~~~~~~~~~~
Called when an interaction has been deleted

Parameters
^^^^^^^^^^
interaction: :class:`Interaction`
    Interaction deleted

on_message_create
~~~~~~~~~~~~~~~~~
Called when a message has been created

.. versionchanged:: 0.0.1a3
    on_message was renamed to on_message_create

Parameters
^^^^^^^^^^
message: :class:`Message`
    Message created

on_message_update
~~~~~~~~~~~~~~~~~
Called when a message has been updated

Parameters
^^^^^^^^^^
message: :class:`Message`
    Message updated

on_message_delete
~~~~~~~~~~~~~~~~~
Called when a message has been deleted

Parameters
^^^^^^^^^^
message: :class:`Message`
    Message deleted

on_partial_message_delete
~~~~~~~~~~~~~~~~~~~~~~~~~
Called when a message has been deleted and cannot be found in the cache

Parameters
^^^^^^^^^^
channel_id: :class:`Snowflake`
    ID of channel
id: :class:`Snowflake`
    ID of the message
guild_id: Optional[:class:`Snowflake`]
    ID of guild if message was not deleted in a :class:`DMChannel`

on_bulk_message_delete
~~~~~~~~~~~~~~~~~~~~~~
Called when messages were deleted in bulk

Parameters
^^^^^^^^^^
messages: List[Union[:class:`Message`, :class:`Snowflake`]]
    List of messages or message ids that were deleted
channel_id: :class:`Snowflake`
    ID of channel were messages were deleted
guild_id: Optional[Snowflake]
    ID of guild if message was not deleted in a :class:`DMChannel`

on_message_pin
~~~~~~~~~~~~~~
Called when a message in a guild has been pinned or unpinned,
not when a pinned message is deleted

Parameters
^^^^^^^^^^
channel: :class:`Channel`
    Channel were message was pinned in
last_pin_timestamp: :obj:`py:datetime.datetime`
    The time at which the most recent pinned message was pinned

on_invite_create
~~~~~~~~~~~~~~~~
Called when an invite for a channel has been created

Parameters
^^^^^^^^^^
invite: :class:`Invite`
    Invite created

on_invite_delete
~~~~~~~~~~~~~~~~
Called when an invite for a channel has been deleted

Parameters
^^^^^^^^^^
channel: Union[:class:`Channel`, :class:`Snowflake`]
    Channel or Channel ID of were invite was deleted
guild: Optional[Union[:class:`Guild`, :class:`Snowflake`]]
    Guild or Guild ID of were invite was deleted
code: :class:`str`
    Code of deleted invite

on_guild_recv
~~~~~~~~~~~~~
Called when an guild a client is already in has been received

Parameters
^^^^^^^^^^
guild: :class:`Guild`
    The guild client is in

on_guild_create
~~~~~~~~~~~~~~~
Called when the client is added to a new guild

Parameters
^^^^^^^^^^
guild: :class:`Guild`
    Guild client has just joined

on_guild_outage
~~~~~~~~~~~~~~~
Called when a guild a client is in is experiencing an outage

Parameters
^^^^^^^^^^
guild: :class:`Guild`
    The client experiencing an outage

on_guild_remove
~~~~~~~~~~~~~~~
Called when client is removed from a guild, e.g client got banned

Parameters
^^^^^^^^^^
guild: :class:`Guild`
    Guild client has been removed from

on_guild_update
~~~~~~~~~~~~~~~
Called when a guild is updated

Parameters
^^^^^^^^^^
guild: :class:`Guild`
    Updated guild

on_guild_ban_add
~~~~~~~~~~~~~~~~
Called when a user has been banned from a guild

Parameters
^^^^^^^^^^
guild: :class:`Guild`
    Guild were user was banned from
user: :class:`User`
    User who was banned

on_guild_ban_remove
~~~~~~~~~~~~~~~~~~~
Called when a banned user has been unbanned

Parameters
^^^^^^^^^^
guild: :class:`Guild`
    Guild were a user has been unbanned
user: :class:`User`
    User who was unbanned

on_guild_emoji_update
~~~~~~~~~~~~~~~~~~~~~
Called when an emoji has been updated

Parameters
^^^^^^^^^^
emoji: :class:`Emoji`
    Emoji that has been updated

on_guild_emojis_update
~~~~~~~~~~~~~~~~~~~~~~
Called when emojis have been updated in bulk,
may be called when a single emoji has been updated.

Parameters
^^^^^^^^^^
emojis: List[:class:`Emoji`]
    List of updated emojis

on_guild_sticker_update
~~~~~~~~~~~~~~~~~~~~~~~
Called when a sticker has been updated

Parameters
^^^^^^^^^^
sticker: :class:`Sticker`
    Sticker updated

on_guild_stickers_update
~~~~~~~~~~~~~~~~~~~~~~~~
Called when stickers have been updated in bulk,
may be called when a single sticker has been updated.

Parameters
^^^^^^^^^^
stickers: List[:class:`Sticker`]
    List of updated stickers

on_guild_integrations_update
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Called when an integration for a guild has been updated

Parameters
^^^^^^^^^^
guild: Union[:class:`Guild`, :class:`Snowflake`]
    Guild were integrations has been updated

on_member_join
~~~~~~~~~~~~~~
Called when a user joins a guild

Parameters
^^^^^^^^^^
member: :class:`Member`
    member object of user who has just joined
guild: :class:`Guild`
    guild were user has joined

on_member_remove
~~~~~~~~~~~~~~~~
Called when a user leaves a guild

Parameters
^^^^^^^^^^
member: Union[:class:`Member`, :class:`User`]
    Member who has just left
guild: Union[:class:`Guild`, :class:`Snowflake`]
    Guild were integrations has been updated

on_member_update
~~~~~~~~~~~~~~~~
Called when a member is updated,
include internal user fields as well

Parameters
^^^^^^^^^^
b_member: :class:`Member`
    Member before updates
a_member: :class:`Member`
    Member after updates
guild: :class:`Guild`
    Guild were member updated in

on_role_create
~~~~~~~~~~~~~~
Called when a role is created in a guild

Parameters
~~~~~~~~~~
role: :class:`Role`
    Created role
guild: :class:`Guild`
    Guild were role was created

on_role_update
~~~~~~~~~~~~~~
Called when a role in a guild is updated

Parameters
^^^^^^^^^^
b_role: :class:`Role`
    Role before updates
a_role: :class:`Role`
    Role after updates
guild: :class:`Guild`
    Guild were role was updated

on_role_delete
~~~~~~~~~~~~~~
Called when a role in a guild is deleted

Parameters
^^^^^^^^^^
role: :class:`Role`
    Role deleted
guild: :class:`Guild`
    Guild were role was deleted

on_guild_scheduled_event_create
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Called when a guild scheduled event is created

Parameters
^^^^^^^^^^
event: :class:`GuildScheduledEvent`
    Event that was created
guild: :class:`Guild`
    Guild that event was created in

on_guild_scheduled_event_update
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Called when a guild scheduled event is updated

Parameters
^^^^^^^^^^
event: :class:`GuildScheduledEvent`
    Event that was updated
guild: :class:`Guild`
    Guild that event was updated in

on_guild_scheduled_event_delete
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Called when a guild scheduled event is deleted

Parameters
^^^^^^^^^^
event: :class:`GuildScheduledEvent`
    Event that was deleted
guild: :class:`Guild`
    Guild that event was deleted in

on_channel_create
~~~~~~~~~~~~~~~~~
Called when a channel is created

Parameters
^^^^^^^^^^
channel: :class:`Channel`
    Channel created

on_channel_update
~~~~~~~~~~~~~~~~~
Called when a channel is updated

Parameters
^^^^^^^^^^
channel: :class:`Channel`
    Channel updated

on_channel_delete
~~~~~~~~~~~~~~~~~
Called when a channel is deleted

Parameters
^^^^^^^^^^
channel: :class:`Channel`
    Channel deleted

on_thread_create
~~~~~~~~~~~~~~~~
Called when a thread is created in a channel

Parameters
^^^^^^^^^^
thread: :class:`Thread`
    Thread that was created

on_thread_update
~~~~~~~~~~~~~~~~
Called when a thread is updated in a channel

Parameters
^^^^^^^^^^
thread: :class:`Thread`
    Thread that was updated

on_thread_delete
~~~~~~~~~~~~~~~~
Called when a thread is deleted in a channel

Parameters
^^^^^^^^^^
thread: :class:`Thread`
    Thread that was deleted

on_thread_sync
~~~~~~~~~~~~~~
Called when a threads sync when client gains access to them

Parameters
^^^^^^^^^^
threads: List[:class:`Thread`]
    List of threads client has gained access to

on_thread_member_update
~~~~~~~~~~~~~~~~~~~~~~~
Called when a thread member has been updated

Parameters
^^^^^^^^^^
member: :class:`ThreadMember`
    Thread member that was updated

on_thread_members_update
~~~~~~~~~~~~~~~~~~~~~~~~
Called when many thread members are updated

Parameters
^^^^^^^^^^
thread: :class:`Thread`
    New thread with updated members

on_voice_state_update
~~~~~~~~~~~~~~~~~~~~~
Called when a members voice state updates

Parameters
^^^^^^^^^^
channel_id: :class:`Snowflake`
    ID of channel member has left or joined,
    ``None`` for left
member: :class:`Member`
    Member object with :class:`VoiceState` attached

on_voice_server_update
~~~~~~~~~~~~~~~~~~~~~~
Called when the client joins a VC.

Parameters
^^^^^^^^^^
voice_connection: :class:`VoiceConnection`
    Connection to voice channel
