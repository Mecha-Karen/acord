.. meta::
   :title: Documentation - Acord [Guides]
   :type: website
   :url: https://acord.readthedocs.io/guides/presences.html
   :description: Guide on how to use presences
   :theme-color: #f54646


*********
Presences
*********
Presences allow for your client to display something about themselves,
or anything you may have in mind.

Classes
-------
* :class:`Presence`
* :class:`Activity`
* :class:`StatusType`
* :class:`ActivityType`

Functions
---------
If the classes are too complicating look no further

* :func:`game`
* :func:`listening`
* :func:`watching`
* :func:`competing`
* :func:`streaming`

Changing presences
------------------
You may have realised theres no change_presence function within :class:`Client`.
Well thats because you need to change the presence per shard,
which can be seen below.

.. code-block:: py

    for shard in Client.shards:
        await shard.change_presence(..., )

Creating your own presences
---------------------------
The main class were looking at is :class:`Presence`.
Your activity which is the fancy text the user sees will be in the :class:`Activity` object.

.. code-block:: py

    presence = Presence(activities=[Activity, Activity])


