.. meta::
   :title: Documentation - Acord [Bases]
   :type: website
   :url: https://acord.readthedocs.io/api/bases.html
   :description: All objects used for the discord API
   :theme-color: #f54646

.. currentmodule:: acord

*****
Bases
*****
Bases are objects which represent different objects in the discord API.
They minify the code written and can help improve readability in your code!

Embed
~~~~~

.. attributetable:: Embed

.. autoclass:: Embed
    :members:

Components
~~~~~~~~~~

.. attributetable:: Component

.. autoclass:: Component
    :members:

ActionRow
=========

.. attributetable:: ActionRow

.. autoclass:: ActionRow
    :members:

Button
======

.. attributetable:: Button

.. autoclass:: Button
    :members:

SelectMenu
==========

.. attributetable:: SelectMenu

.. autoclass:: SelectMenu
    :members:


SelectOption
============

.. attributetable:: SelectOption

.. autoclass:: SelectOption
    :members:

PermissionsOverwrite
~~~~~~~~~~~~~~~~~~~~

.. attributetable:: PermissionsOverwrite

.. autoclass:: PermissionsOverwrite
    :members:

AllowedMentions
~~~~~~~~~~~~~~~

.. attributetable:: AllowedMentions

.. autoclass:: AllowedMentions
    :members:

Flags
~~~~~

BaseFlagMeta
============
.. autoclass:: BaseFlagMeta
    :members: __call__

Intents
=======

.. autoclass:: Intents
    :members:

Users
=====

.. autoclass:: UserFlags
    :members:

Permissions
===========

.. autoclass:: Permissions
    :members:

SystemChannelFlags
==================

.. autoclass:: SystemChannelFlags
    :members:
    :undoc-members:

MessageFlags
============

.. autoclass:: MessageFlags
    :members:
    :undoc-members:

Enums
~~~~~

GuildMessageNotification
========================

.. autoclass:: GuildMessageNotification
    :members:
    :undoc-members:

ExplicitContentFilterLevel
==========================

.. autoclass:: ExplicitContentFilterLevel
    :members:
    :undoc-members:

MFALevel
========

.. autoclass:: MFALevel
    :members:
    :undoc-members:

NSFWLevel
=========

.. autoclass:: NSFWLevel
    :members:
    :undoc-members:

PremiumTierLevel
================

.. autoclass:: PremiumTierLevel
    :members:
    :undoc-members:

VerificationLevel
=================

.. autoclass:: VerificationLevel
    :members:
    :undoc-members:

ComponentTypes
==============

.. autoclass:: ComponentTypes
    :members:
    :undoc-members:

ButtonStyles
============

.. autoclass:: ButtonStyles
    :members:
    :undoc-members:

InteractionType
===============

.. autoclass:: InteractionType
    :members:
    :undoc-members:

ApplicationCommandType
======================

.. autoclass:: ApplicationCommandType
    :members:
    :undoc-members:

InteractionCallback
===================

.. autoclass:: InteractionCallback
    :members:
    :undoc-members:

ChannelTypes
============

.. autoclass:: ChannelTypes
    :members:
    :undoc-members:

VoiceQuality
============

.. autoclass:: VoiceQuality
    :members:
    :undoc-members:

ActivityType
============

.. autoclass:: ActivityType
    :members:
    :undoc-members:

File
~~~~

.. attributetable:: File

.. autoclass:: File
    :members:

Presence
~~~~~~~~
If working with the direct class itself is abit too much for you,
consider using our helping functions.

.. autofunction:: game

.. autofunction:: listening

.. autofunction:: watching

.. autofunction:: competing

.. autofunction:: streaming

.. attributetable:: Presence

.. autoclass:: Presence
    :members:

Activity
========

.. attributetable:: Activity

.. autoclass:: Activity
    :members:



