from __future__ import annotations
import asyncio
from typing import Any

from aiohttp import web
from .abc import InteractionServer as BaseServer
from acord.models import Interaction

try:
    from orjson import loads
except ImportError:
    from json import loads

try:
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError

    nacl_imported = True
except ImportError:
    nacl_imported = False


def handle_incoming_request(client, public_key):
    verify_key = VerifyKey(bytes.fromhex(public_key))

    async def _handler(request: web.Request) -> Any:

        try:
            signature = request.headers["X-Signature-Ed25519"]
            timestamp = request.headers["X-Signature-Timestamp"]
            body = await request.text()

            verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        except BadSignatureError:
            return web.Response(
                body="BAD REQUEST",
                status=401,
                reason="Invalid header values"
            )
        except KeyError:
            return web.Response(
                body="BAD REQUEST",
                status=400,
                reason="Invalid headers"
            )
        data = loads(body)

        if data["type"] == 1:
            interaction = Interaction(conn=client.http, **data)

            await client._dispatch_interaction(interaction)

            return web.Response(body='{"type": 1}')

    return _handler


class InteractionServer(BaseServer):
    """Default implementation of an interaction server

    .. rubric:: Example Usage

    .. code-block:: py

        from acord.rest import InteractionServer, RestApi

        server = InteractionServer(..., )
        rest = RestApi(..., )

        await server.setup(rest, "PUBLIC_KEY")
        await rest.setup(..., )

        server.run_server()
        # Tada your server is now running and can accept requests

    Parameters
    ----------
    host: :class:`str`
        Host to run server on
    port: :class:`int`
        Port to run server on
    endpoint_route: :class:`str`
        Route for interaction,
        defaults to ``/interactions``
    application: :class:`~aiohttp.web.Application`
        An application which the user has already defined
    **kwds:
        Additional kwargs for :class:`~aiohttp.web.Application`,
        IF you have not provided the ``server`` param.
    """
    _internal: dict = {}

    def __init__(
        self,
        **kwds
    ) -> None:
        if not nacl_imported:
            raise ImportError("PyNaCl is not installed")

        application = kwds.pop("server", None)
        application_kwds = {
            i: kwds[i] for i in kwds if i not in BaseServer.__annotations__
        }
        kwds = {i: kwds[i] for i in kwds if i not in application_kwds}

        if not application:
            application = web.Application(**application_kwds)

        kwds["application"] = application

        super().__init__(**kwds)

    async def setup(self, client, public_key) -> None:
        self.application.router.add_route(
            "POST", self.endpoint_route, 
            handle_incoming_request(
                client,
                public_key
            )
        )

        self._internal.update({
            "client": client,
            "setup": True
        })

    def run_server(self, **kwds) -> None:
        client = self._internal.get("client", None)

        assert client is not None, "Server has not been setup"

        kwds.update({
            "loop": client.loop,
            "host": self.host,
            "port": self.port
        })

        web.run_app(self.application, **kwds)

    @property
    def is_setup(self) -> bool:
        return self._internal.get("setup", False)
