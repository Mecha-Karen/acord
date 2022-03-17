# An ABC for any REST related objects
from __future__ import annotations

from abc import ABC, abstractmethod, abstractproperty
from typing import Any
from pydantic import BaseModel


class InteractionServer(ABC, BaseModel):
    """An ABC for creating interaction servers

    .. note::
        Endpoint defaults to ``http://host:port/interactions``

    .. rubric:: Implementing Interaction Servers

    from acord.rest.abc import InteractionServer
    from acord.rest import RestApi

    .. code-block:: py

        class MyServer(InteractionServer):
            ## Implement methods

        server = MyServer(..., )
        rest = RestApi(..., server=server)

        ## Should be done before setup is called
        rest.register_application_command(..., )

        async def main():
            await rest.setup()

        ...
    """
    host: str
    """ Host to run server off of """
    port: int
    """ Port to run server off of """

    endpoint_route: str = "/interactions"
    """ Route endpoints should be received from """
    server: Any = None
    """Server this client is currently using.

    .. DANGER::
        This param may be set but server must be an instance of :class:`~aiohttp.web.Application`.
        Or any object which mirrors the functionality of this object.

        .. note::
            If your using the ABC and not a default implementation,
            this may be whatever you like.

            Else consider passing any parameters for :class:`~aiohttp.web.Application`
            as kwargs.
    """

    @abstractmethod
    async def setup(self, **kwds) -> None:
        """|coro|

        Setups server class,
        ready to be ran.

        Parameters
        ----------
        runner: :class:`dict`
            Kwargs for :class:`~aiohttp.web.AppRunner`
        site: :class:`dict`
            Kwargs for :class:`~aiohttp.web.TCPSite`
        """

    @abstractmethod
    async def run_server(self, **kwds) -> None:
        """|coro|

        Runs server,
        any additional kwargs may be passed.
        """

    @abstractproperty
    def is_setup(self) -> bool:
        """ Whether the server has been setup """
