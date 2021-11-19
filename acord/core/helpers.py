"""
All version related info for connecting to the gateway.
"""
from functools import wraps
from ..core.signals.gateway import INTERNAL_STORAGE
import yarl
from typing import Optional, Literal

API_VERSION = 9
BASE_API_URL = "https://discord.com/api"
GATEWAY_ENCODING = Literal["JSON", "ETF"]


def buildURL(*paths, **parameters) -> str:
    URI = f'{BASE_API_URL}/v{API_VERSION}'
    for path in paths:
        URI += f'/{path}'

    if not parameters:
        return URI

    URI += '?'

    for key, value in parameters.items():
        URI += f'{key}={value}&'

    return yarl.URL(URI)


# Should be used for caching response objects which return on call
def cacheit(section: str, store = INTERNAL_STORAGE, maxItems = 1000):
    def inner(func):
        if section not in store:
            store[section] = set()

        @wraps(func)
        def inner(*args, **kwargs):
            res = func(*args, **kwargs)
            
            if len(store[section]) >= maxItems:
                store[section] = store[section][:maxItems - 1]

            store[section].update([res])

            return res
        return inner

    return inner


class Route(object):
    """ Simple object representing a route """
    def __init__(self, method: str = "GET", *paths, path="/", **parameters):
        if path:
            paths = path.split('/')
        
        self.paths = paths          # Building url with yarn
        self.path = '/'.join(paths)
        self.parameters = parameters
        self.method = method
        self.url = buildURL(*paths, **parameters)

        self.channel_id: Optional[int] = parameters.get('channel_id')
        self.guild_id: Optional[int] = parameters.get('guild_id')
        self.webhook_id: Optional[int] = parameters.get('webhook_id')
        self.webhook_token: Optional[str] = parameters.get('webhook_token')

    @property
    def bucket(self):
        return f'{self.channel_id}:{self.guild_id}:{self.path}'
