"""
All version related info for connecting to the gateway.
"""
from functools import wraps
import yarl
from typing import Optional, Literal, Type, Union

API_VERSION = 10
BASE_API_URL = "https://discord.com/api"
GATEWAY_ENCODING = Literal["JSON", "ETF"]
DISCORD_EPOCH = 1420070400000


def buildURL(*paths, **parameters) -> Union[str, yarl.URL]:
    URI = f"{BASE_API_URL}/v{API_VERSION}"
    for path in paths:
        URI += f"/{path}"

    if not parameters:
        return URI

    URI += "?"

    for key, value in parameters.items():
        if value:
            URI += f"{key}={value}&"

    return yarl.URL(URI)


def isInt(snowflake) -> bool:
    try:
        int(snowflake)
    except ValueError:
        return False
    return True


# Should be used for caching response objects which return on call
def cacheit(section: str, store: dict, maxItems=1000):
    def inner(func):
        if section not in store:
            store[section] = set()

        @wraps(func)
        def inner(*args, **kwargs):
            res = func(*args, **kwargs)

            if len(store[section]) >= maxItems:
                store[section] = store[section][: maxItems - 1]

            store[section].update([res])

            return res

        return inner

    return inner


class Route(object):
    """Simple object representing a route"""

    def __init__(
        self, method: str = "GET", bucket: dict = dict(), *paths, path="/", **parameters
    ):
        if path:
            paths = path.split("/")

        self.paths = paths  # Building url with yarn
        self.path = "/".join(paths)
        self.parameters = parameters
        self.method = method
        self.url = buildURL(*paths, **parameters)

        self.channel_id: Optional[int] = bucket.get("channel_id")
        self.guild_id: Optional[int] = bucket.get("guild_id")
        self.webhook_id: Optional[int] = bucket.get("webhook_id")
        self.webhook_token: Optional[str] = bucket.get("webhook_token")

    @property
    def bucket(self):
        return f"{self.channel_id}:{self.guild_id}:{self.path}"
