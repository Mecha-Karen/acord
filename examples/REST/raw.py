# Basic implementation of working with the REST API
# At a lower level then using the RestAPI class
from __future__ import annotations
import asyncio

from acord.core.http import HTTPClient
from acord.core.abc import Route
from acord import (
    DefaultCache,
    Snowflake,
    Guild,
    User
)


class ClientCache:
    cache = DefaultCache()
    user = None


REST_API = HTTPClient(
    client=ClientCache(),
    token="NzQxNzE0NTcxNjYzNzY5NjUw.Xy7lhg.OwCAYokltjlw3P2_ceIvCDd2M68",
    # Actual token goes above
)

async def get_guild(guild_id: Snowflake, /) -> Guild:
    """ Fetches a guild from the REST API """
    r = await REST_API.request(
        Route("GET", path=f"/guilds/{guild_id}")
    )

    return Guild(conn=REST_API, **(await r.json()))

async def main():
    d = await REST_API.login()
    REST_API.client.user = User(conn=REST_API, **d)

    guild = await get_guild(740523643980873789)
    # Actual guild ID above

    print("Fetched Guild:\n\n", guild)

# Weird issue with asyncio.run
# Raises RuntimeError
loop = asyncio.get_event_loop()
loop.run_until_complete(loop.create_task(main()))
