"""
All version related info for connecting to the gateway.
"""
from typing import Literal, Optional

import yarl

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

        self.channel_id: Optional[...] = parameters.get('channel_id')
        self.guild_id: Optional[...] = parameters.get('guild_id')
        self.webhook_id: Optional[...] = parameters.get('webhook_id')
        self.webhook_token: Optional[str] = parameters.get('webhook_token')

    @property
    def bucket(self):
        return f'{self.channel_id}:{self.guild_id}:{self.path}'
